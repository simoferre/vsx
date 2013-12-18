# VSX
A python library and CLI to inspect CORAID disks mounted on libvirt domains.

Usage of `vsx` cli
------------------
```bash
vsx info [ <guest> ] [ -a ]
vsx mask show <guest>
vsx mask (set | rm) <guest> [ <host> ]
vsx snap show [ <guest> ]
vsx lv <lvname>
vsx (suspend | resume) [ <shelf> ]
vsx csv
```
## Install

### Global installation
```bash
git clone git@git.galliera.it:virtualization/vsx.git
cd vsx
sudo pip install -r requirements.txt
sudo python setup.py install
```

### Inside a virtualenv
```bash
git clone git@git.galliera.it:virtualization/vsx.git
cd vsx
virtualenv .
. bin/activate
pip install -r requirements.txt
python setup.py install
```

## Documentation
To generate documentation use epydoc packages:

```bash
cd path/to/vsx
epydoc --html -o docs vsx.py
```
Read epydoc manual for other output formats and options:

```bash
epydoc -h
```
To install the epydoc package on:

```bash
sudo pip install epydoc
```
or download the installation package from [Epydoc](http://epydoc.sourceforge.net/) and follow the instructions.