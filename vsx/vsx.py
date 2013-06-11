# -*- coding: utf-8 -*-

"""
Info su lun e lv del VSX
"""

from re import match, IGNORECASE
import requests
import simplejson as json
from config import esm_server, esm_user, esm_password, esm_port, SHELVES
from syslog import syslog


class VSX(object):
    """
    Class representing VSXes
    """

    def __init__(self):
        """
        The VSX constructor. It logs on the ESM, stores
        the cookies and fetch all luns info presents on
        the VSX aplliances.
        """

        user = esm_user
        password = esm_password
        url = self.url('admin')
        params = {'op': 'login',
                  'username': user,
                  'password': password}

        # Login and acquire cookie
        resp = requests.post(url, params=params, verify=False)
        self.cookies = dict(JSESSIONID=resp.cookies['JSESSIONID'])

        self.luns = []
        self.fetchluns()

    def url(self, path):
        """
        Build a url.
        @return: a properly configured url.
        """

        return 'https://' + esm_server + ':' + esm_port + '/' + path

    def post(self, bodylist):
        """
        Perform the actual POST query to the ESM.

        @param bodylist: a list of bodydict (aka POST operation)
        @type bodylist: list of dicts

        @return: the POST response.
        """

        url = self.url('configure')
        headers = {'content-type': 'application/json'}

        response = requests.post(url,
                                 cookies=self.cookies,
                                 data=json.dumps(bodylist),
                                 headers=headers,
                                 verify=False)

        if response.status_code != 200:
            syslog('request body: ' + response.request.body)
            syslog(str(response.status_code) + ': ' + response.text)

        return response

    def fetchluns(self):
        """
        Fetch luns info. Gather all informations in self.luns.
        """

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
        """
        Return a Logical Unit from either a LUN or a LV.
        IMPORTANT: It returns only the LU of type 'vsxlun'.

        @return: a dict containing all the info for a LU.
        @rtype: dict
        """

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

    def _mask(self, operation, lvlist, server):
        """
        Actually perform a (rm)mask operation.

        @param operation: it can be either 'remove' or 'add'
        @param lvlist: the lv list to mask
        @param server: the server name, needed to obtain the
                       related macaddresses.
        """

        macs = self.hwaddr(server)
        body = []

        op = {"remove": "vRmmask", "add": "vMask"}

        for lv in lvlist:
            vsxshelf = self.lu(lv=lv)['vsxshelf']
            args = ' '.join([lv] + macs)
            body.append({"op": op[operation], "addr": vsxshelf, "args": args})

        response = self.post(body)
        syslog(response.text)

    def rmmask(self, lvlist, server):
        """
        Remove masks (if needed)

        @param lvlist: the lv list to mask
        @param server: the server name, needed to obtain the
                       related macaddresses.
        """

        self._mask("remove", lvlist, server)

    def setmask(self, lvlist, server):
        """
        Set masks (if needed)

        @param lvlist: the lv list to mask
        @param server: the server name, needed to obtain the
                       related macaddresses.
        """

        self._mask("add", lvlist, server)


import unittest


class TestVSX(unittest.TestCase):

    def setUp(self):
        self.vsx = VSX()
        self.lu = self.vsx.lu(lv="testlv")
        self.server = "mirrina"
        self.macs = {self.server: [u"001b21185d84", u"001517783fd0"]}

        self.testlv = {
            u"status": u"online",
            u"index": 55,
            u"eladdr": u"5100002590311e00",
            u"vsxlun": True,
            u"srxlun": False,
            u"shelf": 105,
            u"lv_os_name": u"testlv",
            u"masks": None,
            u"vsxshelf": "96",
            u"vsxIndex": 2359,
            u"snapshotCount": 0,
            u"mode": u"read/write",
            u"idPath": u"shelfEladdr=5100002590311e00&vsxlun=2359",
            u"lv": u"testlv",
            u"owner": None,
            u"serverAccessMode": u"Unrestricted",
            u"objectType": u"nsObject",
            u"config": u"",
            u"serial": u"e50b01d55c6eec1afc68",
            u"pool": u"pool00",
            u"size": 0
        }

    def test_lu(self):
        self.assertEqual(self.vsx.lu(lun="105.55"), self.lu)
        self.assertEqual(self.testlv["lv"], self.lu["lv"])

    def test_hwaddr(self):
        self.assertEqual(self.vsx.hwaddr(self.server), self.macs[self.server])

    def test_mask(self):
        pass

if __name__ == "__main__":
    unittest.main()
