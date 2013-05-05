"""
This module is built to keep track of all the machines connected to the server
"""
import time
import datetime
import uuid
from collections import deque

from .hashmanager import *

# Dictionary with the machine's UUID as the key
machines = {}

class Machine:
    """
    Represents a single machine connected to the server.
    Calculates stats on the machine
    """
    def __init__(self, instance_type):
        self.uuid = str(uuid.uuid4())
        self.workshares_complete = 0
        self.ipaddr = None
        self.lastcontacttime = None
        self.firstcontacttime = None
        self.workshares = {}
        self.hashes = 0
        self.hashrate = 0
        self.work_start = 0
        self.work_time = 0
        self.instance_type = instance_type

    def _calc_hashrate(self):
        """
        Recalculate the hashrate and store it in self.hashrate
        """
        uptime = self.uptime()
        # We haven't initialized yet
        if uptime is None:
            self.hashrate = 0

        now = time.time()
        # If we are currently working update the cummulative work time
        if self.work_start != 0:
            self.work_time += now - self.work_start
            self.work_start = now
        self.hashrate = self.hashes / self.work_time

    def complete_workshare(self, workshare_hash, start, num_hashes):
        """
        Register completion of a workshare
        """
        try:
            workshare = self.workshares[(workshare_hash, start)]
        except KeyError:
            return None

        self.workshares_complete += 1
        self.hashes += num_hashes
        self.contact()
        del self.workshares[(workshare_hash, start)]

        # We are no longer working, so we will update work_time and set
        # work_start to 0
        if len(self.workshares) == 0:
            self.work_time += time.time() - self.work_start
            self.work_start = 0
        self._calc_hashrate()

    def add_workshare(self, workshare):
        """
        Assign a new workshare to this machine
        """
        self.workshares[(workshare.hashstring, workshare.start)] = workshare
        # If we're not already working, then start
        if self.work_start == 0:
            self.work_start = time.time()

    def free_workshares(self):
        """
        Recycle all currently active workshares on this machine
        """
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
            "hashrate": "%d hashes/s" % self.hashrate,
            "type": instance_types[self.instance_type][0],
            "lastcontact": _sec_to_string(self.lastcontact())}

# We have to import this here to prevent a circular dependency
from .amazon import instance_types

# Simple method for turning a time in seconds into a human friendly format
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
