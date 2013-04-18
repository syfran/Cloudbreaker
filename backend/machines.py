"""
This module is built to keep track of all the machines connected to the server
"""
import time

machines = {}

class machine:
    """
    Represents a single machine connected to the server.
    Calculates stats on the machine
    """
    def __init__(self, apikey):
        self.apikey = apikey
        self.workshares = 0
        self.hashes = 0

    def add_workshare(self, hashes):
        """
        Register completion of a workshare
        """
        self.workshares += 1
        self.hashes += hashes
        self.contact()

    def contact(self):
        """"
        Register contact from this machine
        """
        now = time.time()
        if self.firstcontact is None:
            self.firstcontact = now
        self.lastcontact = now


    def hashRate(self):
        """
        Calculate the average hashrate of the machine 
        """
        return hashes/self.uptime()

    def uptime(self):
        """
        Calculate the time this machine has been up
        """
        return time.time() - self.firstcontact

    def lastcontact(self):
        """
        Calculate the time since the last contact
        """
        return time.time() - self.lastcontact

    def to_dict(self):
        return {
            "ip":self.ipaddr, "type":self.machinetype, "hashrate":self.hashRate(),
            "workshares":self.workshares, "uptime":self.uptime(),
            "lastcontact":self.lastcontact() }
