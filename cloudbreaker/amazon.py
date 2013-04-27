"""
Interface with amazon ec2
"""

import boto.ec2
import datetime

conn = None

def init_boto():
    """
    Establish a connection to amazon aws with our credentials
    """
    global conn

    # us-east-1 and eu-west-1 are the only areas that have gpu
    conn = boto.ec2.connect_to_region("eu-west-1")

def get_spot_price():
    price = conn.get_spot_price_history(instance_type="cg1.4xlarge", 
        product_description="Linux/UNIX", 
        start_time=datetime.datetime.now().isoformat())[0].price
    return price

def new_instance(machinetype, price, number, uuid):
    pass

def kill_instance(uuid):
    pass
