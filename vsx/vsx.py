# -*- coding: utf-8 -*-

"""
Info su lun e lv del VSX
"""

from re import match, IGNORECASE
import requests
import simplejson as json
from config import esm_server, esm_user, esm_password, esm_port, SHELVES
import libxml2
import os
from syslog import syslog


class VSX(object):
    """
    Class representing VSXes
    """

    def __init__(self):

        user = esm_user
        password = esm_password
        url = self.url('admin')
        params = {'op': 'login',
                  'username': user,
                  'password': password}

        # Login and acquire cookie
        resp = requests.post(url, params=params, verify=False)
        self.cookies = dict(JSESSIONID=resp.cookies['JSESSIONID'])

        self.fetchluns()

    def url(self, path):

        return 'https://' + esm_server + ':' + esm_port + '/' + path

    def post(self, bodylist):

        url = self.url('configure')
        headers = {'content-type': 'application/json'}

        response = requests.post(url,
                             cookies=self.cookies,
                             data=json.dumps(bodylist),
                             headers=headers,
                             verify=False)

        #print dir(response)
        print response.url
        print dir(response.request)
        print response.request.body
        print response.text
        return response

    def fetchluns(self):
        # Fetch luns info

        url = self.url('fetch')

        self.luns = []

        for shelf in SHELVES:

            params = {'shelf': shelf, 'vsxlun': ''}
            resp = requests.get(url,
                                params=params,
                                cookies=self.cookies,
                                verify=False)

            info = json.loads(resp.text)[0][1]['reply']

            # Now add the info about the VSX shelf number
            for el in info:
                el.update({u'vsxshelf': shelf})

            self.luns += info

    def lu(self, lun=None, lv=None):

        if lun:
            (shelf, index) = map(int, lun.split('.'))
            for lu in self.luns:
                if (
                    lu['index'] == index and
                    lu['shelf'] == shelf and
                    lu['vsxlun']
                ):
                    return lu
        if lv:
            for lu in self.luns:
                if (
                    lu['lv'] == lv and
                    lu['vsxlun']
                ):
                    return lu

    def hwaddr(self, server=None):
        """
        Return server's mac addresses
        """

        if server is None:
            raise Exception("Cannot set mask: `server´")

        url = self.url('fetch')
        params = {'hba': '', 'groups': ''}

        resp = requests.get(url,
                            params=params,
                            cookies=self.cookies,
                            verify=False)

        info = json.loads(resp.text)[0][1]['reply']

        return [elem['macAddr'] for elem in info if elem['server'] == server]

    def printluns(self, alun=None):
        """
        Stampa le info di alun (o di tutte le lun per default)
        """

        print "-" * 56
        print "%-5s %21s %11s %10s %s" % ('lun', 'lv', 'size', 'pool', 'snaps')
        print "-" * 56

        for lun in self.luns:
            lunindex = [lun['shelf'], lun['index']]
            if not alun or lunindex == map(int, alun.split('.')):
                print "%3s.%-4s %18s %8d GB %10s %5d" % (
                      lun['shelf'], lun['index'], lun['lv'],
                      lun['size']/1000, lun['pool'], lun['snapshotCount'])

    def printlv(self, lvs=None):
        """
        Stampa le info di lvs (o di tutti i lv per default)
        """

        def lvmatch(regex, lvs):
            """
            Ritorna True se la regex matcha lvs
            """
            return match(regex, lvs, IGNORECASE) is not None

        if not lvs:
            return

        regex = '^%s$' % lvs

        if lvs.startswith('*') and lvs.endswith('*'):
            lvs = lvs.replace('*', '')
            regex = ".*%s.*$" % lvs
        elif lvs.startswith('*'):
            lvs = lvs.replace('*', '')
            regex = ".*%s$" % lvs
        elif lvs.endswith('*'):
            lvs = lvs.replace('*', '')
            regex = "^%s.*" % lvs

        print regex

        print "-" * 56
        print "%-5s %21s %11s %10s %s" % ('lun', 'lv', 'size', 'pool', 'snaps')
        print "-" * 56

        for lun in self.luns:
            if lvmatch(regex, lun['lv']):
                print "%3s.%-4s %18s %8d GB %10s %5d" % (
                      lun['shelf'], lun['index'], lun['lv'],
                      lun['size']/1000, lun['pool'], lun['snapshotCount'])

    def rmmask(self, lv, server):
        """
        To be refactored
        """
        pass


    def setmask(self, lvlist, server):
        """
        """

        macs = self.hwaddr(server)
        body = []

        for lv in lvlist:
            vsxshelf = self.lu(lv=lv)['vsxshelf']
            args = ' '.join([lv] + macs)
            body.append({"op": "vMask", "addr": vsxshelf, "args": args})

        response = self.post(body)
        syslog(response.text)


def main():
    import pprint

    #pp = pprint.PrettyPrinter(indent=4)

    vsx = VSX()

    #lvlist = [vsx.lu(lun=lun)['lv']
    #          for lun in luns(libxml2.parseFile('log.xml'))]

    #pp.pprint(vsx.lu(lv='log'))

    lvs = [u'logstriped', u'logdata']
    server = 'doom'

    vsx.setmask(lvs, server)
    #print lvlist, vsx.hwaddr('pong')

if __name__ == "__main__":
    main()
