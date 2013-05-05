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
                      echo "python /home/ubuntu/cloudbreaker/amiscripts/cpu.py&" >> /etc/rc.local
                      echo "exit 0" >> /etc/rc.local
                      /etc/rc.local
                    """

gpu_userdata =     """#! /bin/bash
                      echo "%s" > /etc/cloudbreaker.conf
                      echo "%s" >> /etc/cloudbreaker.conf
                      git clone %s /home/ubuntu/cloudbreaker
                      echo "cd /home/ubuntu/cloudbreaker && git pull" > /etc/rc.local
                      echo "python /home/ubuntu/cloudbreaker/amiscripts/gpu.py&" >> /etc/rc.local
                      echo "python /home/ubuntu/cloudbreaker/amiscripts/cpu.py&" >> /etc/rc.local
                      echo "exit 0" >> /etc/rc.local
                      /etc/rc.local
                    """

# Key is the amazon name
# value is (user friendly name, ami_id, userdata)
instance_types = {
    "t1.micro":("Free Tier", cpu_ami, cpu_userdata),
    "cc2.8xlarge":("Cluster cpu", cluster_ami, cpu_userdata),
    "cg1.4xlarge":("Cluster gpu", cluster_ami, gpu_userdata)}

# Address of the server this will run on
cloudbreaker_server_addr = "syfran.com:6543"

# Amazon reagion to run in. Currently only us-east-1 and eu-west-1 have gpu instances available
aws_region = "us-east-1"

# Key pair for ssh on your amazon aws account
# This shouldn't be needed in general, but helps with developement
keypair = "login.cs"

# Git repository that is used to pull the amiscripts
cloudbreaker_git = "-b ami-refactor git://github.com/syfran/Cloudbreaker.git"

def init_boto():
    """
    Establish a connection to amazon aws with our credentials
    """
    global conn

    # us-east-1 and eu-west-1 are the only areas that have gpu
    conn = boto.ec2.connect_to_region(aws_region)

def get_spot_price(instance_type):
    """
    Gets the latest spot price for the given instance type
    """
    price = conn.get_spot_price_history(instance_type=instance_type, 
        product_description="Linux/UNIX", 
        start_time=datetime.datetime.now().isoformat())[0].price
    return price


def new_instances(number, spot, price, instance_type):
    """
    Requests new instances of the given type and price
    """
    # We can't take advantage of the amazon's number argument
    # because we have to give each one it's own key
    for x in range(0, number):
        machine = Machine(instance_type)

        # lookup user data and ami based on instance type
        userdata = instance_types[instance_type][2] % (cloudbreaker_server_addr, machine.uuid, cloudbreaker_git)
        ami_id = instance_types[instance_type][1]
        try:
            # Determine if we need to create a spot instance
            if spot:
                # If we don't specify a price then get the current spotprice
                if price is None:
                    price = conn.get_spot_price_history()[0].price
                # Request the instance and store the id
                spot_requests = conn.request_spot_instances(price, 
                    ami_id, instance_type=instance_type, key_name=keypair, user_data=userdata)
                machine.aws_id = spot_requests[0].id
            else:
                # Request a generic instance
                instance_request = conn.run_instances(ami_id, instance_type=instance_type, 
                    key_name=keypair, user_data=userdata)
                machine.aws_id = instance_request.instances[0].id
        # If we have a problem connecting then just drop it
        except boto.exception.EC2ResponseError:
            return

        machine.is_spot = spot

        # Store the machine instance
        machines[machine.uuid] = machine
        
def kill_instance(uuid): 
    """
    Attempt to terminate the machine with the given uuid and
    remove it from the interface
    """
    machine = machines[uuid]
    try:
        if machine.is_spot:
            # If it is a spot instance then we will get the instance_id from
            # the spot request and cancel request for good measure
            r = conn.get_all_spot_instance_requests(request_ids=[machine.aws_id])[0]
            instance_id = r.instance_id
            r.cancel()
        else:
            instance_id = machine.aws_id
        conn.terminate_instances(instance_ids=[instance_id])
    except boto.exception.EC2ResponseError:
        pass

    # Finally we can free the workshares to be recycled and remove the instace
    # from our list
    machine.free_workshares()
    del machines[uuid]
