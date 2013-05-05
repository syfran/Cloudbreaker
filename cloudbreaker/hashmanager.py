"""
Keep track of hashes and workshares
"""
from Queue import Queue, Empty
import time

# synchronized queue of hashtrackers
hash_queue = Queue()
# All hashes known, key is the hash string
# Hash strings are assumed to be unique
hashes = {}

# This dictionary contains all possible PasswordSources. It is used to generate
# the user interface
sources = {}
# This is a list of possible password hashes. It is used to generate the user
# interface
hashtypes = ["sha512"]

class PasswordSource:
    """
    This class represents a generator of candidate passwords
    """
    def __init__(self, name, fullname, size):
        self.name = name
        self.fullname = fullname
        self.size = size

def get_workshare(size):
    """
    This function gets the next possible workshare from our list of hashes
    """
    share = None
    hash_ = None

    # We want to loop until we find a workshare
    while share is None:
        # Try to get a hash from the queue, we wait two seconds in case it is
        # removed by another request, and then gives up and returns None
        try:
            hash_ = hash_queue.get(timeout=2)
        except Empty:
            return None

        # Since we never directly remove from the queue, we have to check if
        # the hash is still in our list of hashes, if it isn't then we don't
        # add it back to the queue
        if hash_.hashstring not in hashes:
            continue

        # If it is a valid hash, then get the workshare
        share = hash_.get_workshare(size)

    # Add our hash back into the queue
    hash_queue.put(hash_)
    return share

def complete_workshare(hash_string, share_size):
    """
    Register a workshare as complete
    """
    # If it isn't in our valid hashes, ignore it
    if hash_string in hashes:
        hash_ = hashes[hash_string]
        hash_.complete_workshare(share_size)

def recycle_workshare(share):
    """
    Add the workshare back into a queue to be redistributed
    """
    try:
        hash_ = hashes[share.hashstring]
    except KeyError:
        return
    hash_.recycle_share(share)

def add_hash(hash_):
    """
    Add a hash to the list of hashes
    """
    if hash_ not in hashes:
        hash_queue.put(hash_)
        hashes[hash_.hashstring] = hash_

def remove_hash(hash_):
    """
    Remove the hash from the list of hashes
    """
    if hash_ in hashes:
        del hashes[hash_]

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
        self.init_time = time.time()

    def to_dict(self):
        """
        Return a dictionary representation of the workshare
        """
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
        self.complete_state = 0
        self.complete = False
        self.password = None
        self.recycled_workshares = []

    def complete_workshare(self, share_size):
        """
        Register the worksahre as complete
        """
        self.complete_state += share_size

    def get_workshare(self, size):
        """
        Get a new workshare for this hash 
        """
        if self.complete:
            return None

        # Check for a perfect match in the recycle list
        for share in self.recycled_workshares:
            if share.size == size:
                self.recycled_workshares.remove(share)
                share.init_time = time.time()
                return share

        # Check if this is the last workshare
        if self.sent_state + size > self.source.size:
            this_sharesize = self.source.size - self.sent_state
            # If we don't have anymore workshares, get the best recycled share
            if this_sharesize == 0:
                # Check for the closest match
                closest = None
                for share in self.recycled_workshares:
                    if abs(size - share.size) < abs(size - closest.size):
                        closest = share
                if closest is not None:
                    closest.init_time = time.time()
                return closest
        else:
            this_sharesize = size

        workshare = Workshare(self.hashstring, 
            self.hashtype, self.source, self.sent_state, this_sharesize)
        self.sent_state += this_sharesize
        return workshare

    def recycle_share(self, share):
        """
        Add the given share to our recycled list
        """
        self.recycled_workshares.append(share)

    def complete_hash(self, password):
        """
        Mark a hash as finished with the given password
        """
        self.complete = True
        self.password = password

    def to_dict(self):
        """
        Turn this object into a dictionary that will be sent to the web
        interface
        """
        return {
            "hash":self.hashstring,
            "password": "" if self.password is None else self.password,
            "progress":"%.1f%%" % ((self.complete_state* 100.0) /self.source.size),
            "type":self.hashtype}
