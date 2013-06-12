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
from domain import luns
from docopt import docopt
from lxml import etree


storage = VSX()


def _lvlist(lus):
    """Return the list of lvs of the guest
    """

    return [storage.lu(lun=l)['lv'] for l in lus]


def listguests():
    """Print a list of all guests
    """
    
    for host in config.HOSTS:

        conn = libvirt.open("qemu+ssh://%s/system" % host)

        print "%s" % host.upper()

        for id in conn.listDomainsID():
            dom = conn.lookupByID(id)

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


def main():
    """The main program
    """

    arguments = docopt(__doc__, version='CLI for VSX 0.1a')

    if arguments["info"]:
        listguests()

if __name__ == '__main__':
    main()
