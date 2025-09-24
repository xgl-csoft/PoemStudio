'''
Write by DogMonkeys
按钮回调及结构
'''

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from PyQt5.QtWidgets import *
from PoemStudioAPI import *
from MainUI import Ui_PoemStudioWin
from FindPoem import Ui_FindPoem
from ViewPoem import Ui_ViewPoem
from PoemGame import Ui_PoemGame
from About import Ui_About
from Help import Ui_Help
from sys import exit, stdout
import time

class PoemStudio(QMainWindow):
	'''
	PoemStudio主类
	继承: QMainWindow
	'''

	def __init__(self):
		self.app = QApplication([])

		super(PoemStudio, self).__init__()
		
		self.ui = Ui_PoemStudioWin()
		self.ui.setupUi(self)
		self.ui.FindPoem.clicked.connect(self.Callback_FindPoem)
		self.ui.act_FindPoem.triggered.connect(self.Callback_FindPoem)
		self.ui.Game.clicked.connect(self.Callback_PoemGame)
		self.ui.act_Game.triggered.connect(self.Callback_PoemGame)
		self.ui.act_Help.triggered.connect(self.Callback_Help)
		self.ui.act_About.triggered.connect(self.Callback_About)
		self.FindPoem = _FindPoem()
		self.PoemGame = _PoemGame()
		self.Help = _Help()
		self.About = _About()

	def Callback_FindPoem(self):
		# 查找按钮的回调
		self.FindPoem.show()

	def Callback_PoemGame(self):
		# 答题的回调
		self.PoemGame.show()

	def Callback_Help(self):
		# 帮助的回调
		self.Help.show()

	def Callback_About(self):
		# 答题的回调
		self.About.show()

	def main(self):
		self.show()
		return self.app.exec_()

class _FindPoem(QMainWindow):
	'''
	查找古诗子类
	'''

	def __init__(self):
		super(_FindPoem, self).__init__()

		self.ui = Ui_FindPoem()
		self.ui.setupUi(self)
		self.ui.MainTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.ui.MainTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.ui.MainTable.setHorizontalHeaderLabels(["古诗名称", "作者/朝代", "链接(古诗文网)"])
		# for i in range(1, 3): #调整列宽
		# 	self.ui.MainTable.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)

		self.ui.Find.clicked.connect(self.search)
		self.ui.MainTable.doubleClicked.connect(self.Callback_ViewPoem)
		self.ViewPoem = _ViewPoem()

	# 搜索回调
	def search(self):
		QMessageBox.information(self, "提示", "为了提高搜索速度,开始搜索后应用将会失去响应,属正常现象")
		t1 = time.time()
		for i in range(self.ui.MainTable.rowCount()):
			self.ui.MainTable.removeRow(0)
		key = self.ui.Input_l.text()
		result = []
		ths = []

		if self.ui.c_title.isChecked():
			# 标题op
			th = PThread(API.getList, (key, SEARCHLINK_TITLE, "title"))
			ths.append(th)
		if self.ui.c_author.isChecked():
			# 作者op
			th = PThread(API.getList, (key, SEARCHLINK_AUTHOR, "author"))
			ths.append(th)
		if self.ui.c_guwen.isChecked():
			# 古文op
			th = PThread(API.getList, (key, SEARCHLINK_GUWEN, "guwen"))
			ths.append(th)

		# 多线程启动,效率+=50%至少 14.3->7.2
		for i in ths:
			i.start()

		for i in ths:
			i.join()

		for i in ths:
			_ret = i.getReturn()
			if _ret:
				result += _ret

		# 如果为空则不会遍历,无需检查
		for (i, data) in enumerate(result):
			self.ui.MainTable.insertRow(i)
			for (j, now) in enumerate(data):
				self.ui.MainTable.setItem(i, j, QTableWidgetItem(now))
		print(time.time() - t1)

	# 双击单元格回调
	def Callback_ViewPoem(self, index):
		title = self.ui.MainTable.item(index.row(), 0).text() # 标题
		author = self.ui.MainTable.item(index.row(), 1).text() # 作者
		url = self.ui.MainTable.item(index.row(), 2).text() # url
		# print(title, author, url)
		self.ViewPoem.config(title=title, url=url, author=author)
		self.ViewPoem.show()

class _ViewPoem(QMainWindow):
	'''浏览古诗子类'''
	def __init__(self):
		super(_ViewPoem, self).__init__()

		self.ui = Ui_ViewPoem()
		self.ui.setupUi(self)
		# self.show()

	# 设置信息,顺便显示了
	def config(self, **config):
		self.url = config["url"]
		try:
			self.content = API.getPoem(self.url)
			self.ui.l_title.setText("古诗名称:" + config["title"])
			self.ui.l_author.setText("古诗作者:" + config["author"])
			self.ui.Show.setText(self.content)
		except Exception as e:
			QMessageBox.critical(self, "错误", "解析古诗时出现异常\n")
			# raise e
			# sys.exit(1)

class _PoemGame(QMainWindow):
	'''古诗答题子类'''
	def __init__(self):
		super(_PoemGame, self).__init__()
		self.ui = Ui_PoemGame()
		self.ui.setupUi(self)
		self.ui.choose.clicked.connect(self.Callback_Choose)
		self.ui.restart.clicked.connect(self.Callback_restart)
		self.ui.next.clicked.connect(self._next)
		self.status = 0 # 0没题,1有题
		self.idx = 0 # 题目指针
		self.crt = 0 # 正确
		self.nc = -1 # 正确的索引数
		self.flg = 0 # 是否为初始状态, 0: 否,1: 是
		self._cs = [self.ui.CA, self.ui.CB, self.ui.CC]
		self.cs = [False, False, False]
		self.ui.CA.toggled.connect(self.checkrdA)
		self.ui.CB.toggled.connect(self.checkrdB)
		self.ui.CC.toggled.connect(self.checkrdC)

	def checkrdA(self, isc):
		self.cs[0] = isc

	def checkrdB(self, isc):
		self.cs[1] = isc

	def checkrdC(self, isc):
		self.cs[2] = isc

	def Callback_Choose(self):
		self.lnk = QInputDialog.getText(self, "输入古诗链接 - PoemStudio", "复制查找页面的链接:")[0] # 状态不要
		try:
			self.title = API.getTitle(self.lnk)
			self.sents = API.cutPoem(API.getPoem(self.lnk))
			print(self.title, self.sents)
			self.config()
		except:
			QMessageBox.critical(self, "异常", "链接错误") # 格式错了,前面已经把标志舍去了

	def config(self):
		self.ui.title.setText("当前古诗:" + self.title)
		self.status = 1

	def Callback_restart(self):
		# 重新开始
		self.idx = 0
		self.crt = 0
		self.flg = 0
		self._next()
		self.ui.label.setText("正确率: %d/%d" % (0, 0)) # 手动设置一下

	def check(self):
		if self.status:
			print("check:idx", self.idx, "crt:", self.crt)
			for i, j in enumerate(self.cs):
				print(i, j)
				if j:
					if i == self.nc:
						# QMessageBox.information(self, "正确", "恭喜您答对了")

						self.crt += 1
						print("self.crt:", self.crt)
						self.ui.label.setText("正确率: %d/%d" % (self.crt, self.idx + 1))
						return
					else:
						print("err_", i, self.nc, self.sents)
						QMessageBox.information(self, "错误", "抱歉,回答错误.\n正确答案是:%s" % self.nowt[self.nc])
						self.ui.label.setText("正确率: %d/%d" % (self.crt, self.idx + 1))
						return
					
			else:
				print("err", i, self.nc)
				QMessageBox.information(self, "错误", "抱歉,回答错误.\n正确答案是:%s" % self.nowt[self.nc])
			self.ui.label.setText("正确率: %d/%d" % (self.crt, self.idx + 1))

	def _next(self):
		try:
			print("next:idx:", self.idx)

			if self.flg:
				self.check()
				self.idx += 1
				print("变更后idx", self.idx)
			if self.idx >= len(self.sents):
				# 古诗末尾
				QMessageBox.information(self, "完成!", "恭喜您完成《%s》的挑战,正确率: %d/%d" % (self.title, self.crt, self.idx))
				return
			text, self.nowt, self.nc = API.randomTest(self.sents, self.idx)
			print(text, self.nowt, self.nc)
			self.ui.test.setText(text)
			for i, j in enumerate(self._cs):
				j.setText(self.nowt[i])
			self.flg = 1
		except Exception as e:
			print(e)
			# raise e

class _Help(QMainWindow):
	'''
	帮助文档类
	'''
	def __init__(self):
		super(_Help, self).__init__()
		self.ui = Ui_Help()
		self.ui.setupUi(self)

class _About(QMainWindow):
	'''
	关于页面类
	'''
	def __init__(self):
		super(_About, self).__init__()
		self.ui = Ui_About()
		self.ui.setupUi(self)

if __name__ == '__main__':
	appctxt = ApplicationContext()
	ps = PoemStudio()
	ps.main()
	exit_code = appctxt.app.exec_()
	exit(exit_code)
