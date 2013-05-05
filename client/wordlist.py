"""
Provide a wordlist as a source for passwords
"""

import tempfile
import subprocess

from config import john_bin, john_conf

# Provide a mapping from the wordlist's name to it's location
wordlist_lookup = {"cain":"/home/ubuntu/cain.txt"}

# Commands
wordlist_slice_cmd = "tail -n +%(start)s %(dict_file)s | head -n %(size)s"
john_mangle_cmd = john_bin + " -pipe -stdout -rules --session=%(session)s-rule"

class Wordlist:
    """
    Represents a wordlist password source. The rules argument may be used to
    specify we don't want to apply rule mangling
    """
    def __init__(self, wordlist_name, start, size, session, rules=True):
        self.cmd_args = {"dict_file": wordlist_lookup[wordlist_name],
                         "start":start,
                         "size":size,
                         "session":session}
        self.rules = rules
        self.devnull = open("/dev/null")

    def get_pipe(self, wordlist=None):
        """
        Return a pipe output of the wordlist. If the wordlist file is given, it
        will also output the list to that file
        """
        slice_proc = subprocess.Popen(wordlist_slice_cmd % self.cmd_args, shell=True,
            stdout=subprocess.PIPE, stderr=self.devnull)
        if self.rules:
            mangle_proc = subprocess.Popen(john_mangle_cmd % self.cmd_args, shell=True,
                stdin = slice_proc.stdout, stdout=subprocess.PIPE,
                stderr=self.devnull)
            out = mangle_proc.stdout
        else:
            out = slice_proc.stdout

        # Use tee to split the wordlist off
        if wordlist is not None:
            save_proc = subprocess.Popen(["tee", wordlist.name], stdin=out, \
                stdout=subprocess.PIPE, stderr=self.devnull)
            out = save_proc.stdout

        return out
