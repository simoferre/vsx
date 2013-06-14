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


# override libvirt's default error handler
def errorHandler(ctx, err):
    pass


libvirt.registerErrorHandler(errorHandler, None)

storage = VSX()


COLORS = {
  'black': '0;30', 'dark gray': '1;30',
  'blue': '0;34', 'light blue': '1;34',
  'green': '0;32', 'light green': '1;32',
  'cyan': '0;36', 'light cyan': '1;36',
  'red': '0;31', 'light red': '1;31',
  'purple': '0;35', 'light purple': '1;35',
  'brown': '0;33', 'yellow': '1;33',
  'light gray':'0;37', 'white': '1;37',
}


FLAGS = {
    'live'           : libvirt.VIR_MIGRATE_LIVE,
    'persistent'     : libvirt.VIR_MIGRATE_PERSIST_DEST,
    'undefinesource' : libvirt.VIR_MIGRATE_UNDEFINE_SOURCE
}


def colored(string, color):
    """
    Fancy terminal color
    """
    return "\x1b[%sm%s\x1b[0m" % (COLORS[color], string)


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


def printguest(dom):
    """Print a guest
    """

    persistent = dom.isPersistent and 'P' or 'N'

    lus = luns(dom)
    lvs = _lvlist(lus)

    strlv = ''
    for lv in lvs:
        lu = storage.lu(lv=lv)
        mask = '!', 'red'
        if lu['masks']:
            mask = '#', 'green'

        strlv += "%s(%s%s) " % (colored(lv, 'white'), 
                                colored(mask[0], mask[1]), 
                                lu[u'snapshotCount'])

    strlu = ' '.join(lus)
    print " {0:1} {1:26} {2:41} {3:40}".format(
        persistent,
        colored(dom.name(), 'light green'), 
        strlu, 
        strlv)


def listguests(guest=None):
    """A guestlist representation
    """

    for host in config.HOSTS:

        conn = libvirt.open("qemu+ssh://%s/system" % host)

        if guest:
            try:
                dom = conn.lookupByName(guest)

                print "%s" % colored(host.upper(), 'light red')
                printguest(dom)

                break
            except libvirt.libvirtError, err:
                continue
        else:
            print "%s" % colored(host.upper(), 'light red')

            for did in conn.listDomainsID():
                dom = conn.lookupByID(did)

                printguest(dom)


def main():
    """The main program
    """

    arguments = docopt(__doc__, version='CLI for VSX 0.1a')

    if arguments["info"]:
        listguests(arguments["<guest>"])

if __name__ == '__main__':
    main()
