"""
This module provides function for interacting with the server
"""
import requests
import sys
import time

import config

class CloudbreakerServer:
    """ 
    This class provides two method for interacting with the server using the
    requests library
    """
    def __init__(self):
        """
        Read in the configuration file
        """
        config.load_config()

    def get_workshare(self, workshare_size):
        """
        Get a new workshare from the server of the given size
        """
        post_params = {"uuid":config.machine_uuid, "size":workshare_size}
        get_workshare_addr = "http://" + config.server_addr + "/getshare"
        share = None
        # Continue to request shares until we get one
        while share is None:
            response = None
            while response is None:
                try:
                    response = requests.post(get_workshare_addr, params=post_params)
                except requests.ConnectionError:
                    response = None
                    time.sleep(10)

            share = response.json
            # If the server sent sleep or we don't have a request, then sleep
            if share is None:
                time.sleep(10)
            elif 'sleep' in share:
                time.sleep(share['sleep'])
                share = None
        return share

    def complete_workshare(self, workshare, num_hashes, password):
        """
        Tell the server that we have completed the workshare password should be
        set to None if one hasn't been found
        """
        post_params = {"uuid":config.machine_uuid, 
            'hash':workshare['hash'],
            'num_hashes':num_hashes,
            'size':workshare['size'],
            'start':workshare['start']}
        if password is not None:
            post_params['password'] = password
        complete_workshare_addr = "http://" + config.server_addr + "/completeshare"
        success = None
        # Continue to try to submit until we get the server
        while success is None:
            try:
                success = requests.post(complete_workshare_addr, params=post_params)
            except requests.ConnectionError:
                success = None
                time.sleep(10)

