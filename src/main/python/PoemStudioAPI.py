'''
Write by DogMonkeys
后端API
'''

from requests import get
from bs4 import BeautifulSoup as bsp
from threading import Thread
from random import shuffle, randint
from copy import deepcopy
import re

SEARCHLINK_TITLE = "https://so.gushiwen.cn/search.aspx?type=title&page=%d&value=%s"
SEARCHLINK_AUTHOR = "https://so.gushiwen.cn/search.aspx?type=author&page=%d&value=%s"
SEARCHLINK_GUWEN = "https://so.gushiwen.cn/search.aspx?type=guwen&page=%d&value=%s"
HREF_HEAD = "https://so.gushiwen.cn"

test = 'https://so.gushiwen.cn/shiwenv_6db49b0261da.aspx'

class API:
	'''
	API给前端调用
	'''

	# 获得网页的省略
	@classmethod
	def getHtml(cls, url):
		response = get(url=url)
		response.encoding = "utf-8"
		return bsp(response.text, "html.parser")

	# 搜索结果
	@classmethod
	def getList(cls, poem, m, t):
		res = []
		print("新的list")
		for i in range(100):
			print(t, ":", i)
			pg = cls.xthread(cls.__getList_1, (i, poem, m, t))
			if pg:
				res += pg
			else:
				break

		# print(res)
		return res

	# 解析原文
	@classmethod
	def getPoem(cls, url):
		page = cls.getHtml(url)
		return page.find_all("div", class_="contson")[0].text

	# 多线程加强版
	@classmethod
	def xthread(cls, func, args):
		th = PThread(func, args)
		th.start()
		th.join()
		return th.getReturn()

	# getList的子线程函数
	@classmethod
	def __getList_1(cls, i, poem, m, t):
		res = []
		try:
			page = cls.getHtml(m % (i+1, poem))
			conts = page.find_all("div", class_="left")[1].find_all("div", class_="cont")
			if len(conts) == 0:
				print("mode %s exit at" % t, i)
				return None
			
			for k in conts:
				ps = k.find_all("p")[0:2]
				a_of_title = ps[0].find_all("a")[0]
				# print(a_of_title)
				href = HREF_HEAD + a_of_title["href"].replace("\n", "") # 链接
				title = a_of_title.text.replace("\n", "") # 标题
				# print(href, title)
				source = ps[1].text.replace("\n", "")
				# print(source)
				res.append((title, source, href))

		except Exception as e:
			print("mode %s exit at" % t, e)
			return None

		return res

	@classmethod
	def cutPoem(cls, _str):
		cts = []
		ret = re.split(r"[,\.\?\!\<\>\(\)\"\'\[\]\{\}\/\\，。？！‘’“”（）【】\s]", _str)
		for i, j in enumerate(ret):
			if j == "":
				# print("xxx")
				cts.append(i)
		for l, k in enumerate(cts):
			del ret[k - l]
		return ret

	@classmethod
	def getTitle(cls, url):
		page = cls.getHtml(url)
		return page.find_all("div", class_="sons")[0].find_all("h1")[0].text

	@classmethod
	def randomTest(cls, sents, idx):
		_type = randint(0, 1) # 0:上句 1:下句
		if idx == 0:
			# 第一句
			_type = 1
		if idx == len(sents) - 1:
			# 最后
			_type = 0
		backup = dict(zip(range(len(sents)), deepcopy(sents)))
		print(backup)
		
		if _type:
			# 下句
			xtext = "题目: '%s'的下一句是?" % backup[idx]
			del backup[idx]
			ctr = backup[idx + 1]
			del backup[idx + 1]
			print("t=1,", backup)
			
		else:
			xtext = "题目: '%s'的上一句是?" % backup[idx]
			del backup[idx]
			ctr = backup[idx - 1]
			del backup[idx - 1]
			print("t=0,", backup)
		ret = [ctr]

		for i in range(2):
			tid = randint(0, len(backup) - 1)
			tid = list(backup.keys())[tid]
			ret.append(backup[tid])
			del backup[tid] # 去重
		shuffle(ret)
		print(ret, ctr)
		print(ret.index(ctr))
		return xtext, ret, ret.index(ctr)

class PThread(Thread):
	'''
	继承自线程类,用于获得返回值
	'''
	def __init__(self, func, args):
		super(PThread, self).__init__()
		self.func = func
		self.args = args

	def run(self):
		self._return = self.func(*self.args)

	def getReturn(self):
		try:
			return self._return
		except:
			return None
