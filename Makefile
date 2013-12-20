prefix=/usr/local
pyver=$(shell python -c "from distutils.sysconfig import get_python_version; print(get_python_version())")
vvver=$(shell python setup.py -V)

all:

dep:
	apt-get install python-setuptools
	apt-get install python-pip
	apt-get install libxml2-dev
	apt-get install libxslt-dev
	apt-get install libpython2.7-dev
	apt-get install zlib1g-dev
	apt-get install pkg-config
	apt-get install libvirt-dev
	apt-get install libvirt-bin
	pip install -r requirements.txt

# Binary stuff
build:
	python setup.py build

install: build
	python setup.py install --prefix=$(prefix)


# Clean from package
distclean:
	-rm vsx/*.pyc
	-rm *.pyc

trashclean:
	-rm bin/*~
	-rm vv/*~
	-rm *~

buildclean:
	-rm -rf build/	

easyclean:
	-rm -rf temp
	-rm -rf VSX.egg-info

# Uninstall
rm:
	-rm $(prefix)/lib/python$(pyver)/dist-packages/VSX-$(vvver)-py$(pyver).egg-info
	-rm -rf $(prefix)/lib/python$(pyver)/dist-packages/VSX-$(vvver)-py$(pyver).egg

clean: distclean buildclean trashclean easyclean rm
