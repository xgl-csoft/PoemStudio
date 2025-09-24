PYTHON = python.exe
PYUIC5 = pyuic5.exe

defult :
	make -r run

build-ui : Makefile
	$(PYUIC5) ../../../ui/About.ui -o About.py
	$(PYUIC5) ../../../ui/FindPoem.ui -o FindPoem.py
	$(PYUIC5) ../../../ui/Help.ui -o Help.py
	$(PYUIC5) ../../../ui/MainUI.ui -o MainUI.py
	$(PYUIC5) ../../../ui/PoemGame.ui -o PoemGame.py
	$(PYUIC5) ../../../ui/ViewPoem.ui -o ViewPoem.py
	$(PYUIC5) ../../../ui/About.ui -o About.py
	$(PYUIC5) ../../../ui/Help.ui -o Help.py

run : Makefile 
	make -r build-ui
	$(PYTHON) main.py
