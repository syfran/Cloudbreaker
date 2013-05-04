"""
This script runs John the ripper with a wordlist and rule mangling
"""
import subprocess
import sys
import tempfile
import multiprocessing

from cloudbreakercli import *

# General configuration
john_conf = "/etc/john/john.conf"
john_bin = "/home/ubuntu/john-run/john"
john_session = "cpu-session"

dict_filename = "/home/ubuntu/cain.txt"

john_mangle_cmd = john_bin + " -pipe -stdout -rules --session=%(session)s-rule | tee %(wordlist)s"

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
    cmd_args["dict"] = dict_filename
    cmd_args["session"] = john_session

    # Generate a bunch of temporary files to write to, they are automatically
    # deleted on close
    with tempfile.NamedTemporaryFile() as passf, tempfile.NamedTemporaryFile() as potf, tempfile.NamedTemporaryFile() as wordlist:

        cmd_args["passfile"] = passf.name
        cmd_args["potfile"] = potf.name
        cmd_args["wordlist"] = wordlist.name

        # Write the hash to our passsword file
        passf.write(share["hash"] + "\n")
        passf.flush()

        # Get a slice of the wordlist
        dict_output = subprocess.Popen("tail -n +%(start)d %(dict)s | head -n %(size)d" % cmd_args, 
            shell=True, stdout=subprocess.PIPE, stderr=devnull)
        # Pass the slice through a rule based mangler
        mangler = subprocess.Popen(john_mangle_cmd % cmd_args, shell=True, 
            stdin=dict_output.stdout, stderr=devnull, stdout=subprocess.PIPE)
        # Run john the ripper on it
        john = subprocess.Popen(john_command % cmd_args, 
            stdin=mangler.stdout, stderr=devnull, stdout=devnull, shell=True)
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
