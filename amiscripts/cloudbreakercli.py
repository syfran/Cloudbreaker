import requests

CONF_PATH = "/etc/cloudbreaker.conf"

class CloudBreakerServer:
    def __init__(self):
        self.config = CloudBreakerConf()


    def connect(self):
        pass

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
