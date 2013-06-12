# -*- coding: utf-8 -*-
"""CLI for VSX

Usage:
  vsxcl.py info [ <guest> ]
  vsxcl.py mask [show | set | rm] <guest> [ <host> ]

  vsxcl.py (-h | --help)
  vsxcl.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

Try:
  vsxcl.py mask set bmdw

"""
import libvirt
import os

from vsx import config
from vsx import VSX
from docopt import docopt
from lxml import etree


storage = VSX()


def luns(dom):
    """Xpath query to retrieve instance's disks from XML
    """

    if isinstance(dom, libvirt.virDomain):
        dom = dom.XMLDesc(0)

    tree = etree.fromstring(dom)
    devices = []

    for disk in tree.xpath("/domain/devices/disk[@device='disk']"):

        try:
            devices.append(disk.xpath("source/@dev")[0])
        except IndexError:
            pass

    return [os.path.basename(dev).strip('e') for dev in devices]


def _lvlist(lus):
    """Return the list of lvs of the guest
    """

    return [storage.lu(lun=l)['lv'] for l in lus]


def printguest(host, dom):
    """Print a guest
    """

    print "%s" % host.upper()

    if dom.isPersistent:
        print "    P",

    lus = luns(dom)
    lvs = _lvlist(lus)

    strlv = ''
    for lv in lvs:
        lu = storage.lu(lv=lv)
        mask = '!'
        if lu['masks']:
            mask = '#'

        strlv += "%s(%s) " % (lv, lu[u'snapshotCount'])

        strlu = ' '.join(lus)
        print "%s %s %s %s" % (mask, dom.name(), strlu, strlv)


def listguests(guest=None):
    """A guestlist representation
    """
    devnull = open(os.devnull, 'w')

    for host in config.HOSTS:

        conn = libvirt.open("qemu+ssh://%s/system" % host)

        if guest:
            try:
                dom = conn.lookupByName(guest)
                printguest(host, dom)
            except libvirt.libvirtError, err:
                continue
        else:
            for did in conn.listDomainsID():
                dom = conn.lookupByID(did)
                printguest(host, dom)


def main():
    """The main program
    """

    arguments = docopt(__doc__, version='CLI for VSX 0.1a')

    if arguments["info"]:
        listguests(arguments["<guest>"])

if __name__ == '__main__':
    main()
