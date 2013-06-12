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
        """The VSX constructor.

        It logs on the ESM, stores
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
        """Build a url.

        @return: a properly configured url.
        """

        return 'https://' + esm_server + ':' + esm_port + '/' + path

    def post(self, bodylist):
        """Perform the actual POST query to the ESM.

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
        """Fetch luns info.

        Gather all informations in self.luns.
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
        """Return a Logical Unit from either a LUN or a LV.

        It returns only the LU of type 'vsxlun'.

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
        """Return server's mac addresses

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

    def _mask(self, operation, lvlist, server, serverlist):
        """Actually perform a (rm)mask operation.

        It takes either a server or a list of servers.

        @param operation: it can be either 'remove' or 'add'
        @param lvlist: the lv list to mask
        @param server: the server name, needed to obtain the
                       related macaddresses.
        @param serverlist: the server name list, needed to obtain the
                           related macaddresses.
        """

        body = []

        if server:
            serverlist = [server, ]

        macs = [mac
                for srv in serverlist
                for mac in self.hwaddr(srv)]

        op = {"remove": "vRmmask", "add": "vMask"}

        for lv in lvlist:
            vsxshelf = self.lu(lv=lv)['vsxshelf']
            args = ' '.join([lv] + macs)
            body.append({"op": op[operation], "addr": vsxshelf, "args": args})

        response = self.post(body)
        syslog(response.text)

        return response

    def rmmask(self, lvlist, server=None, serverlist=[]):
        """Remove masks (if needed).

        @param lvlist: the lv list to mask
        @param server: the server name, needed to obtain the
                       related macaddresses.
        @param serverlist: the server name list, needed to obtain the
                           related macaddresses.
        """

        return self._mask("remove", lvlist, server, serverlist)

    def setmask(self, lvlist, server=None, serverlist=[]):
        """Set masks (if needed).

        @param lvlist: the lv list to mask
        @param server: the server name, needed to obtain the
                       related macaddresses.
        @param serverlist: the server name list, needed to obtain the
                           related macaddresses.
        """

        return self._mask("add", lvlist, server, serverlist)


import unittest


class TestVSX(unittest.TestCase):

    def setUp(self):

        self.vsx = VSX()
        self.lu = self.vsx.lu(lv="testlv1")

        self.server = "mirrina"
        self.macs = {self.server: [u"001b21185d84", u"001517783fd0"]}

        self.testlv = {
            u"status": u"online",
            u"index": 55,
            u"eladdr": u"5100002590311e00",
            u"vsxlun": True,
            u"srxlun": False,
            u"shelf": 105,
            u"lv_os_name": u"testlv1",
            u"masks": None,
            u"vsxshelf": "96",
            u"vsxIndex": 2359,
            u"snapshotCount": 0,
            u"mode": u"read/write",
            u"idPath": u"shelfEladdr=5100002590311e00&vsxlun=2359",
            u"lv": u"testlv1",
            u"owner": None,
            u"serverAccessMode": u"Unrestricted",
            u"objectType": u"nsObject",
            u"config": u"",
            u"serial": u"e50b01d55c6eec1afc68",
            u"pool": u"pool00",
            u"size": 0
        }

    def test_lu(self):
        """
        """

        self.assertEqual(self.vsx.lu(lun="105.55"), self.lu)
        self.assertEqual(self.testlv["lv"], self.lu["lv"])

    def test_hwaddr(self):
        """
        """

        self.assertEqual(self.vsx.hwaddr(self.server), self.macs[self.server])

    def test_1_server_1_lv_mask(self):
        """
        Test mask to one exsisting LV on one server
        """

        resp = self.vsx.setmask([self.lu["lv"], ], self.server)
        self.assertEqual(resp.status_code, 200)

        resp = self.vsx.rmmask([self.lu["lv"], ], self.server)
        self.assertEqual(resp.status_code, 200)

    def test_2_servers_1_lv_mask(self):
        """
        Test mask to one exsisting LV on two servers
        """

        server2 = "pacman"

        resp = self.vsx.setmask([self.lu["lv"], ],
                                serverlist=[self.server, server2])
        self.assertEqual(resp.status_code, 200)

        resp = self.vsx.rmmask([self.lu["lv"], ],
                               serverlist=[self.server, server2])
        self.assertEqual(resp.status_code, 200)

    def test_2_servers_2_lvs_mask(self):
        """
        Test mask to two exsisting LV on two servers
        """

        server2 = "pacman"
        lv2 = "testlv2"

        resp = self.vsx.setmask([self.lu["lv"], lv2],
                                serverlist=[self.server, server2])
        self.assertEqual(resp.status_code, 200)

        resp = self.vsx.rmmask([self.lu["lv"], lv2],
                               serverlist=[self.server, server2])
        self.assertEqual(resp.status_code, 200)

    def test_twice_mask(self):
        """
        Test mask twice the same lv
        """
        resp = self.vsx.setmask([self.lu["lv"], ], self.server)
        self.assertEqual(resp.status_code, 200)

        # Set the same mask
        resp = self.vsx.setmask([self.lu["lv"], ], self.server)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.ok)

        js = resp.json()

        self.assertEqual(js["metaCROp"], "noAction")
        self.assertEqual(js["configState"], "completedFailed")
        self.assertEqual(js["message"],
                         "mask 001b21185d84 exists on LV testlv1")

        resp = self.vsx.rmmask([self.lu["lv"], ], self.server)
        self.assertEqual(resp.status_code, 200)

    def test_rm_unmasked_lun(self):
        """
        Try to unmask a non-masked lv
        """

        resp = self.vsx.rmmask([self.lu["lv"], ], self.server)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.ok)

        js = resp.json()

        self.assertEqual(js["metaCROp"], "noAction")
        self.assertEqual(js["configState"], "completedFailed")
        self.assertEqual(js["message"],
                         "mask 001b21185d84 does not exist on LV testlv1")

if __name__ == "__main__":
    unittest.main()
