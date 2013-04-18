"""
Keep track of hashes and workshares
"""

hashes = []

class workshare:
    """
    Class to encapsulate workshares
    """
    def __init__(self, hashstring, crackmodule, start, size):
        self.hashstring = hashstring
        self.crackmodule = crackmodule
        self.start = start
        self.size = size

class hashtracker:
    """
    Represent a submitted hash
    """

    def __init__(self, hashstring, crackmodule):
        self.hashstring = hashstring
        self.crackmodule = crackmodule

    def get_workshare(self):
        """
        Get a new workshare for this hash
        """
        pass

    def to_dict(self):
        return {
            "hash":self.hashstring, "progress":self.progress,
            "type":self.crackmodule.modtype()}
