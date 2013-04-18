"""
This module is built to keep track of all the machines connected to the server
"""
import time
import uuid

machines = {}

class machine:
    """
    Represents a single machine connected to the server.
    Calculates stats on the machine
    """
    def __init__(self):
        self.uuid = uuid.uuid4()
        self.workshares = 0
        self.hashes = 0
        self.ipaddr = None
        self.lastcontacttime = None
        self.firstcontacttime = None
        self.machinetype = None
        self.workshare = None

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
        if self.firstcontacttime is None:
            self.firstcontacttime = now
        self.lastcontacttime = now


    def hashRate(self):
        """
        Calculate the average hashrate of the machine 
        """
        uptime = self.uptime()
        if uptime is None:
            return None
        return self.hashes/self.uptime()

    def uptime(self):
        """
        Calculate the time this machine has been up
        """
        if self.firstcontacttime is None:
            return None
        return time.time() - self.firstcontacttime

    def lastcontact(self):
        """
        Calculate the time since the last contact
        """
        if self.lastcontacttime is None:
            return None
        return time.time() - self.lastcontacttime

    def to_dict(self):
        """
        Return a dictionary representation of this object
        """
        return {
            "ip":self.ipaddr, "type":self.machinetype, "hashes":self.hashes, 
            "hashrate":self.hashRate(), "workshares":self.workshares,
            "uptime":self.uptime(), "lastcontact":self.lastcontact() }
