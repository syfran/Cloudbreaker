"""
Keep track of hashes and workshares
"""
from Queue import Queue, Empty

# synchronized queue of hashtrackers
hash_queue = Queue()
# All hashes known, key is the hash string
# Hash strings are assumed to be unique
hashes = {}

sources = {}
hashtypes = ["sha512"]

class PasswordSource:
    def __init__(self, name, fullname, size, mult):
        self.name = name
        self.fullname = fullname
        self.size = size
        self.hash_multiplier = mult

def get_workshare(size):
    share = None
    hash_ = None

    while share is None:
        try:
            hash_ = hash_queue.get(timeout=2)
        except Empty:
            return None

        if hash_.hashstring not in hashes:
            return None

        share = hash_.get_workshare(size)

    hash_queue.put(hash_)
    return share

def add_hash(hash_):
    if hash_ not in hashes:
        hash_queue.put(hash_)
        hashes[hash_.hashstring] = hash_

def remove_hash(hash_):
    if hash_.hashstring in hashes:
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

    def get_workshare(self, size):
        """
        Get a new workshare for this hash 
        """
        if self.complete:
            return None

        if self.sent_state + size > self.source.size:
            this_sharesize = self.source.size - self.sent_state
            if this_sharesize == 0:
                return None
        else:
            this_sharesize = size

        workshare = Workshare(self.hashstring, 
            self.hashtype, self.source, self.sent_state, this_sharesize)
        self.sent_state += this_sharesize
        return workshare

    def complete_hash(self, password):
        self.complete = True
        self.password = password

    def to_dict(self):
        return {
            "hash":self.hashstring[:10] + "..",
            "password": "" if self.password is None else self.password,
            "type":self.hashtype}
