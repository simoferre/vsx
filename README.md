# VSX
A python library and CLI to inspect CORAID disks mounted on libvirt domains.

## Usage of `vsx` cli

```bash
vsx info [ <guest> ] [ -a ]
vsx mask show <guest>
vsx mask (set | rm) <guest> [ <host> ]
vsx snap show [ <guest> ]
vsx lv <lvname>
vsx (suspend | resume) [ <shelf> ]
vsx csv
vsx pvs
vsx pools
```

## Install

On a Debian machine:

```bash
git clone git@git.galliera.it:virtualization/vsx.git
cd vsx
sudo make dep
```
Edit the file `vsx/config.py` with the esm hostname,
the esm user and password, the hosts and the vsx shelves you want
to manage and then run

```bash
sudo make install
```

As an alternative, you can install the program manually running:

```bash
sudo python setup.py install
```

But keep in mind that you have to provide the following dependencies:

- setuptools
- pip
- libxml2
- libxslt
- libpython2.7
- zlib1g
- pkg-config
- libvirt-dev
- libvirt-bin


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