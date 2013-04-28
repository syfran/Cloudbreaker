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
            response = None
            while response is None:
                try:
                    response = requests.post(get_workshare_addr, params=post_params)
                except requests.ConnectionError:
                    response = None
                    time.sleep(10)

            share = response.json()
            if 'sleep' in share:
                time.sleep(share['sleep'])
                share = None
        return share

    def complete_workshare(self, workshare, password=None):
        post_params = {"uuid":self.config.get_uuid(), 
            'hash':workshare['hash'],
            'start':workshare['start']}
        if password is not None:
            post_params['password'] = password
        complete_workshare_addr = "http://" + self.config.get_server() + "/completeshare"
        success = None
        while success is None:
            try:
                success = requests.post(complete_workshare_addr, params=post_params)
            except requests.ConnectionError:
                success = None
                time.sleep(10)

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
