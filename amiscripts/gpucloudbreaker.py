"""
This module utilizes oclHashcat to crack passwords
"""
import subprocess
import sys
import tempfile

from cloudbreakercli import *

# General configuration
john_conf = "/etc/john/john.conf"
john_bin = "/home/ubuntu/john-run/john"

john_session = "gpu-session"

oclHashcat_bin = "/home/ubuntu/oclHashcat/cudaHashcat-plus64.bin"

dict_filename = "/home/ubuntu/cain.txt"

john_mangle_cmd = john_bin + " -pipe -stdout -rules --session=%(session)s | tee %(wordlist)s"

oclHashcat_cmd = oclHashcat_bin + " --disable-potfile -m %(format_num)s -o %(outfile)s --outfile-format=2 %(passfile)s"

workshare_size = 20000

devnull = open('/dev/null', 'w')

server = CloudBreakerServer()
while True:
    share = server.get_workshare(workshare_size)

    cmd_args = share
    cmd_args["format"] = "sha512crypt"
    cmd_args["format_num"] = "1800"
    cmd_args["dict"] = dict_filename
    cmd_args["session"] = john_session

    # Write to temporary files that will be erased on close
    with tempfile.NamedTemporaryFile() as passf, tempfile.NamedTemporaryFile() as outfile, tempfile.NamedTemporaryFile() as wordlist:

        cmd_args["passfile"] = passf.name
        cmd_args["outfile"] = outfile.name
        cmd_args["wordlist"] = wordlist.name

        # Write our hash to a password file
        passf.write(share["hash"] + "\n")
        passf.flush()

        # Read a slice of the dictionary
        dict_output = subprocess.Popen("tail -n +%(start)d %(dict)s | head -n %(size)d" % cmd_args, 
            shell=True, stdout=subprocess.PIPE, stderr=devnull)
        # Pass it through a mangler
        mangler = subprocess.Popen(john_mangle_cmd % cmd_args, shell=True, 
            stdin=dict_output.stdout, stderr=devnull, stdout=subprocess.PIPE)
        # Run cudaHashcat-plus on the wordlist
        hashcat = subprocess.Popen(oclHashcat_cmd % cmd_args, 
            stdin=mangler.stdout, stderr=devnull, stdout=devnull, shell=True)
        hashcat.wait()
        password = outfile.readline().strip()

        num_hashes = 0

        # Find the number of passwords tried
        if password == "":
            password = None
            num_hashes = subprocess.check_output(['wc', '-l', wordlist.name]).split(' ')[0]
        else:
            num_hashes = subprocess.check_output(['grep', '-xn', password, wordlist.name]).split(':')[0]
        server.complete_workshare(share, num_hashes, password)
