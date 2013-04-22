"""
Keep track of hashes and workshares
"""
from queue import Queue

hash_queue = Queue()
hashes = {}

def get_workshare():
    share = None
    hash_ = None

    while share is None:
        try:
            hash_ = hash_queue.get(timeout=2)
        except EmptyException:
            return None

        if hash_.hashstring not in hashes:
            return None

        share = hash_.get_workshare()

    hash_queue.put(hash_)
    return share

def add_hash(hash_):
    hash_queue.put(hash_)
    hashes[hash_.hashstring] = hash_

def remove_hash(hash_):
    del hashes[hash_.hashstring]

class Workshare:
    """
    Class to encapsulate workshares
    """
    def __init__(self, hashstring, hashtype, passwordsource, start, size):
        self.hashstring = hashstring
        self.hashtype = hashtype
        self.passwordsource = passwordsource
        self.start = start
        self.size = size
    def to_dict(self):
        return {"hash":self.hashstring, "type":self.hashtype, "source":self.passwordsource.name,
            "start":self.start, "size":self.size}

class HashTracker:
    """
    Represent a submitted hash
    """

    def __init__(self, hashstring, hashtype, source):
        self.hashstring = hashstring
        self.hashtype = hashtype
        self.source = source
        self.sent_state = 0
        self.complete = False
        self.password = None

        # hard coded for now
        self.sharesize = 30000

    def get_workshare(self):
        """
        Get a new workshare for this hash 
        """
        if self.complete:
            return None

        if self.sent_state + self.sharesize > self.source.size:
            this_sharesize = self.source.size - self.sent_state
        else:
            this_sharesize = self.sharesize

        workshare = Workshare(self.hashstring, 
            self.hashtype, self.source, self.sent_state, this_sharesize)
        self.sent_state += this_sharesize
        return workshare

    def complete_hash(self, password):
        self.complete = True
        self.password = password

    def to_dict(self):
        return {
            "hash":self.hashstring, "password":self.password, "type":self.hashtype}
