"""
Keep track of hashes and workshares
"""

hashes = []

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

class HashTracker:
    """
    Represent a submitted hash
    """

    def __init__(self, hashstring, hashtype, source):
        self.hashstring = hashstring
        self.hashtype = hashtype
        self.source = source
        self.state = 0

        # hard coded for now
        self.sharesize = 30000
        self.lock = Lock()

    def get_workshare(self):
        """
        Get a new workshare for this hash """ # Keep this synchronized
        with lock:
            if self.state + self.hashsize > self.source.size:
                this_sharesize = self.source.size - self.state
            else:
                this_sharesize = self.sharesize
            workshare = Workshare(self.hashstring, 
                self.hashtype, self.source, self.state, this_sharesize)
            self.state += this_sharesize

    def get_progress(self):
        return 

    def to_dict(self):
        return {
            "hash":self.hashstring, "progress":self.progress,
            "type":self.crackmodule.modtype()}
