import subprocess
import sys
import tempfile

from cloudbreakercli import *

john_conf = "/etc/john/john.conf"
john_bin = "/home/ubuntu/john-run/john"

dict_filename = "/home/ubuntu/cain.txt"

john_mangle_cmd = john_bin + " -pipe -stdout -rules"

john_command = john_bin + " -pipe --format=%(format)s --nolog --pot=%(potfile)s %(passfile)s"

workshare_size = 100

devnull = open('/dev/null', 'w')

server = CloudBreakerServer()
while True:
    share = server.get_workshare(workshare_size)

    cmd_args = share
    cmd_args["format"] = "sha512crypt"
    cmd_args["dict"] = dict_filename

    with tempfile.NamedTemporaryFile() as passf, tempfile.NamedTemporaryFile() as potf:
        cmd_args["passfile"] = passf.name
        cmd_args["potfile"] = potf.name

        passf.write(share["hash"] + "\n")
        passf.flush()

        dict_output = subprocess.Popen("tail -n +%(start)d %(dict)s | head -n %(size)d" % cmd_args, 
            shell=True, stdout=subprocess.PIPE, stderr=devnull)
        mangler = subprocess.Popen(john_mangle_cmd, shell=True, 
            stdin=dict_output.stdout, stderr=devnull, stdout=subprocess.PIPE)
        john = subprocess.Popen(john_command % cmd_args, 
            stdin=mangler.stdout, stderr=devnull, stdout=devnull, shell=True)
        john.wait()
        password = potf.readline().split(':')[-1][:-1]
        if password == "":
            password = None
        server.complete_workshare(share, password)
