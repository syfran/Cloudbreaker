"""
Configuration variables for coudbreaker client
"""

# Server config variables
conf_path = "/etc/cloudbreaker.conf"
server_addr = None
machine_uuid = None


john_conf = "/etc/john/john.conf"
john_bin = "/home/ubuntu/john-run/john"

oclHashcat_bin = "/home/ubuntu/oclHashcat/cudaHashcat-plus64.bin"



def load_config():
    """
    Load the configuration file into the variables. Waits until the file can be
    successfully loaded
    """
    global server_addr
    global machine_uuid
    while server_addr is None or machine_uuid is None:
        try:
            with open(config.conf_path, 'r') as conffile:
                server_addr = conffile.readline().strip()
                machine_uuid = conffile.readline().strip()
        except IOError:
            server_addr = None
            _uuid = None
            if wait == 0:
                return False
            else:
                time.sleep(wait)