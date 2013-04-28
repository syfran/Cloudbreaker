"""
Interface with amazon ec2
"""
import boto.exception
import boto.ec2
import datetime
from .machines import *

conn = None

cloudbreaker_server_addr = "syfran.com:6543"
instance_type = "t1.micro"
ami_id = "ami-250f6d4c"
aws_region = "us-east-1"
keypair = "login.cs"

def init_boto():
    """
    Establish a connection to amazon aws with our credentials
    """
    global conn

    # us-east-1 and eu-west-1 are the only areas that have gpu
    conn = boto.ec2.connect_to_region(aws_region)

def get_spot_price():
    price = conn.get_spot_price_history(instance_type=instance_type, 
        product_description="Linux/UNIX", 
        start_time=datetime.datetime.now().isoformat())[0].price
    return price

def new_instances(number=1, spot=True, price=None):
    for x in range(0, number):
        machine = Machine()
        userdata = """#! /bin/bash
                      echo "%s" > /etc/cloudbreaker.conf
                      echo "%s" >> /etc/cloudbreaker.conf""" % (cloudbreaker_server_addr, machine.uuid)
        try:
            if spot:
                if price is None:
                    price = conn.get_spot_price_history()[0].price
                print("Getting on spot for %d" % price)
                spot_requests = conn.request_spot_instances(price, 
                    ami_id, instance_type=instance_type, key_name=keypair, user_data=userdata)
                machine.aws_id = spot_requests[0].id
            else:
                print("Getting on demand (hopefully)")
                instance_request = conn.run_instances(ami_id, instance_type=instance_type, 
                    key_name=keypair, user_data=userdata)
                machine.aws_id = instance_request.id
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
        return

    machine.free_workshares()
    del machines[uuid]
