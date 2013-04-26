"""
This module is built to keep track of all the machines connected to the server
"""
import time
import datetime
import uuid

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

    def complete_workshare(self, workshare_hash, start):
        """
        Register completion of a workshare
        """
        del self.workshares[(workshare_hash, int(start))]
        self.workshares_complete += 1
        self.contact()

    def add_workshare(self, workshare):
        self.workshares[(workshare.hashstring, workshare.start)] = workshare

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
            "workshares":self.workshares_complete,
            "uptime": _sec_to_string(self.uptime()),
            "openshares":len(self.workshares),
            "lastcontact": _sec_to_string(self.lastcontact())}

def _sec_to_string(seconds):
    if seconds is None:
        return "Never"
    minutes,seconds = divmod(seconds, 60)
    hours,minutes = divmod(minutes, 60)
    days,hours = divmod(hours, 24)
    returnstr = ""
    if days != 0:
        returnstr += "%d days " % days
    if hours != 0:
        returnstr += "%d hours " % hours
    if minutes != 0:
        returnstr += "%d minutes " % minutes
    returnstr += "%.1f seconds" % seconds
    return returnstr
