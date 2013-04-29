import subprocess
import sys
import tempfile

from cloudbreakercli import *

john_conf = "/etc/john/john.conf"
john_bin = "/home/ubuntu/john-run/john"

dict_filename = "/home/ubuntu/cain.txt"
john_recfile = "/home/ubuntu/john-run/john.rec"

john_mangle_cmd = john_bin + " -pipe -stdout -rules | tee %(wordlist)s"

john_command = john_bin + " -pipe --format=%(format)s --nolog --pot=%(potfile)s %(passfile)s"

workshare_size = 2000

devnull = open('/dev/null', 'w')

server = CloudBreakerServer()
while True:
    share = server.get_workshare(workshare_size)

    cmd_args = share
    cmd_args["format"] = "sha512crypt"
    cmd_args["dict"] = dict_filename

    with tempfile.NamedTemporaryFile() as passf, tempfile.NamedTemporaryFile() as potf, tempfile.NamedTemporaryFile() as wordlist:

        cmd_args["passfile"] = passf.name
        cmd_args["potfile"] = potf.name
        cmd_args["wordlist"] = wordlist.name

        passf.write(share["hash"] + "\n")
        passf.flush()

	# make sure the rec file is gone
	subprocess.call(["rm", "-f", john_recfile])

        dict_output = subprocess.Popen("tail -n +%(start)d %(dict)s | head -n %(size)d" % cmd_args, 
            shell=True, stdout=subprocess.PIPE, stderr=devnull)
        mangler = subprocess.Popen(john_mangle_cmd % cmd_args, shell=True, 
            stdin=dict_output.stdout, stderr=devnull, stdout=subprocess.PIPE)
        john = subprocess.Popen(john_command % cmd_args, 
            stdin=mangler.stdout, stderr=sys.stderr, stdout=sys.stderr, shell=True)
        john.wait()
        password = potf.readline().split(':')[-1][:-1]

        num_hashes = 0

        if password == "":
            password = None
            num_hashes = subprocess.check_output(['wc', '-l', wordlist.name]).split(' ')[0]
        else:
            num_hashes = subprocess.check_output(['grep', '-xn', password, wordlist.name]).split(':')[0]
        server.complete_workshare(share, num_hashes, password)
