"""
Interface with amazon ec2
"""
import boto.exception
import boto.ec2
import datetime

from .machines import *

conn = None

cpu_ami = "ami-0dcfad64"
cluster_ami = "ami-4f7b1926"
cpu_userdata =     """#! /bin/bash
                      echo "%s" > /etc/cloudbreaker.conf
                      echo "%s" >> /etc/cloudbreaker.conf
                      git clone %s /home/ubuntu/cloudbreaker
                      echo "cd /home/ubuntu/cloudbreaker && git pull" > /etc/rc.local
                      echo "python /home/ubuntu/cloudbreaker/amiscripts/cpucloudbreaker.py&" >> /etc/rc.local
                      echo "exit 0" >> /etc/rc.local
                      /etc/rc.local
                    """

gpu_userdata =     """#! /bin/bash
                      echo "%s" > /etc/cloudbreaker.conf
                      echo "%s" >> /etc/cloudbreaker.conf
                      git clone %s /home/ubuntu/cloudbreaker
                      echo "cd /home/ubuntu/cloudbreaker && git pull" > /etc/rc.local
                      echo "python /home/ubuntu/cloudbreaker/amiscripts/gpucloudbreaker.py&" >> /etc/rc.local
                      echo "python /home/ubuntu/cloudbreaker/amiscripts/cpucloudbreaker.py&" >> /etc/rc.local
                      echo "exit 0" >> /etc/rc.local
                      /etc/rc.local
                    """
# Key is the amazon name
# value is (user friendly anem, ami_id, userdata)
instance_types = {
    "t1.micro":("Free Tier", cpu_ami, cpu_userdata),
    "cc2.8xlarge":("Cluster cpu", cluster_ami, cpu_userdata),
    "cg1.4xlarge":("Cluster gpu", cluster_ami, gpu_userdata)}

cloudbreaker_server_addr = "syfran.com:6543"
aws_region = "us-east-1"
keypair = "login.cs"

cloudbreaker_git = "git://github.com/syfran/Cloudbreaker.git"
def init_boto():
    """
    Establish a connection to amazon aws with our credentials
    """
    global conn

    # us-east-1 and eu-west-1 are the only areas that have gpu
    conn = boto.ec2.connect_to_region(aws_region)

def get_spot_price(instance_type):
    price = conn.get_spot_price_history(instance_type=instance_type, 
        product_description="Linux/UNIX", 
        start_time=datetime.datetime.now().isoformat())[0].price
    return price

def new_instances(number, spot, price, instance_type):
    for x in range(0, number):
        machine = Machine(instance_type)

        # lookup user data and ami based on instance type
        userdata = instance_types[instance_type][2] % (cloudbreaker_server_addr, machine.uuid, cloudbreaker_git)
        ami_id = instance_types[instance_type][1]
        try:
            if spot:
                if price is None:
                    price = conn.get_spot_price_history()[0].price
                spot_requests = conn.request_spot_instances(price, 
                    ami_id, instance_type=instance_type, key_name=keypair, user_data=userdata)
                machine.aws_id = spot_requests[0].id
            else:
                instance_request = conn.run_instances(ami_id, instance_type=instance_type, 
                    key_name=keypair, user_data=userdata)
                machine.aws_id = instance_request.instances[0].id
        except boto.exception.EC2ResponseError:
            return

        machine.is_spot = spot
        machines[machine.uuid] = machine
        
def kill_instance(uuid):
    machine = machines[uuid]

    try:
        if machine.is_spot:
            r = conn.get_all_spot_instance_requests(request_ids=[machine.aws_id])[0]
            instance_id = r.instance_id
            r.cancel()
        else:
            instance_id = machine.aws_id
        conn.terminate_instances(instance_ids=[instance_id])
    except boto.exception.EC2ResponseError:
        pass

    machine.free_workshares()
    del machines[uuid]
