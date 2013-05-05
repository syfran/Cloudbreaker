"""
This script runs John the ripper with a wordlist and rule mangling
"""
import subprocess
import sys
import tempfile
import multiprocessing

from server import CloudbreakerServer
from config import john_conf, john_bin
from wordlist import Wordlist


# General configuration
john_session = "cpu-session"

dict_filename = "/home/ubuntu/cain.txt"

john_command = john_bin + " -pipe --format=%(format)s --nolog --pot=%(potfile)s --session=%(session)s %(passfile)s"

# This hack allows us to get a smaller workshare if we're on a t1.micro
# instance
if multiprocessing.cpu_count() > 2:
    workshare_size = 5000
else:
    workshare_size = 300

devnull = open('/dev/null', 'w')

server = CloudBreakerServer()
while True:
    share = server.get_workshare(workshare_size)

    # These will be used to fill in the various commands
    cmd_args = share
    cmd_args["format"] = "sha512crypt"
    cmd_args["session"] = john_session

    # Generate a bunch of temporary files to write to, they are automatically
    # deleted on close
    with tempfile.NamedTemporaryFile() as passf, tempfile.NamedTemporaryFile() \
        as potf, tempfile.NamedTemporaryFile() as wordlist_output:

        cmd_args["passfile"] = passf.name
        cmd_args["potfile"] = potf.name

        # Write the hash to our passsword file
        passf.write(share["hash"] + "\n")
        passf.flush()

        wordlist = Wordlist("cain", share["start"], share["size"], john_session)
        mangler_out = wordlist.get_pipe(wordlist_output)
        # Run john the ripper on it
        john = subprocess.Popen(john_command % cmd_args, 
            stdin=mangler_out, stderr=devnull, stdout=devnull, shell=True)
        john.wait()
        # See if there is anything in the pot file
        password = potf.readline().split(':')[-1][:-1]

        num_hashes = 0

        if password == "":
            # If there is no password, then we did as many hashes as is in the
            # wordlist
            password = None
            num_hashes = subprocess.check_output(['wc', '-l', wordlist.name]).split(' ')[0]
        else:
            # If we did find the hash then we can find the number of hashes
            # based on its position in the wordlist
            num_hashes = subprocess.check_output(['grep', '-xn', password, wordlist.name]).split(':')[0]
        server.complete_workshare(share, num_hashes, password)
