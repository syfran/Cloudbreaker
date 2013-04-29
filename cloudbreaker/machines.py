"""
This module is built to keep track of all the machines connected to the server
"""
import time
import datetime
import uuid
from collections import deque

from .hashmanager import *

machines = {}

class Machine:
    """
    Represents a single machine connected to the server.
    Calculates stats on the machine
    """
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.workshares_complete = 0
        self.ipaddr = None
        self.lastcontacttime = None
        self.firstcontacttime = None
        self.workshares = {}
        self.hashes = 0
        self.pause_start = time.time()
        self.paused_time = 0

    def complete_workshare(self, workshare_hash, start, num_hashes):
        """
        Register completion of a workshare
        """
        workshare = self.workshares[(workshare_hash, start)]
        self.workshares_complete += 1
        self.hashes += num_hashes
        self.contact()
        del self.workshares[(workshare_hash, start)]
        if len(self.workshares) == 0 and self.pause_start == 0:
            self.pause_start = time.time()

    def add_workshare(self, workshare):
        self.workshares[(workshare.hashstring, workshare.start)] = workshare
        if self.pause_start != 0:
            self.paused_time += time.time() - self.paused.start
            self.paused.start = 0

    def free_workshares(self):
        for share in self.workshares.values():
            recycle_workshare(share)

    def contact(self):
        """"
        Register contact from this machine
        """
        now = time.time()
        if self.firstcontacttime is None:
            self.firstcontacttime = now
        self.lastcontacttime = now

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
            "ip": "" if self.ipaddr is None else self.ipaddr,
            "uuid":self.uuid,
            "workshares":self.workshares_complete,
            "uptime":_sec_to_string(self.uptime()),
            "openshares":len(self.workshares),
            "hashrate": "%d hashes/s" % (self.hashes / (self.uptime() - self.paused_time)),
            "lastcontact": _sec_to_string(self.lastcontact())}

def _sec_to_string(seconds):
    if seconds is None:
        return "Never"
    minutes,seconds = divmod(seconds, 60)
    hours,minutes = divmod(minutes, 60)
    days,hours = divmod(hours, 24)
    returnstr = ""
    if days != 0:
        returnstr += "%dd" % days
    if hours != 0:
        returnstr += "%dh" % hours
    if minutes != 0:
        returnstr += "%dm" % minutes
    returnstr += "%.0fs" % seconds
    return returnstr
