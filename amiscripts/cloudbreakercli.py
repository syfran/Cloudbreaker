from __future__ import print_function
import requests
import sys
import time

CONF_PATH = "/etc/cloudbreaker.conf"

class CloudBreakerServer:
    def __init__(self):
        self.config = CloudBreakerConf()

    def get_workshare(self, workshare_size):
        post_params = {"uuid":self.config.get_uuid(), "size":workshare_size}
        get_workshare_addr = "http://" + self.config.get_server() + "/getshare"
        share = None
        while share is None:
            try:
                response = requests.post(get_workshare_addr, params=post_params)
            except requests.ConnectionError:
                print("Error connecting to server", file=sys.stderr)
                return None
            share = response.json()
            if 'sleep' in share:
                time.sleep(share['sleep'])
                share = None
        return share

class CloudBreakerConf:
    def __init__(self):
        self._server = None
        self._uuid = None
        self.exists = False

        self._readconf()

    def _readconf(self):
        try:
            with open(CONF_PATH, 'r') as conffile:
                self._server = conffile.readline().strip()
                self._uuid = conffile.readline().strip()
                self.exists = True
        except IOError:
            pass

    def get_server(self):
        if self._server is None:
            self._readconf()
        return self._server

    def get_uuid(self):
        if self._uuid is None:
            self._readconf()
        return self._uuid
