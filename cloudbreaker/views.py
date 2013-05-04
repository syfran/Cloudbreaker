"""
This module contains all possible HTTP pages
"""
from pyramid.view import view_config
from pyramid.httpexceptions import *
from pyramid.response import Response
from pyramid.security import forget, authenticated_userid

from .hashmanager import *
from .machines import machines
from .amazon import *

@view_config(context=HTTPForbidden)
def auth_test(request):
    """
    If a view raises HTTPForbidden this will force a password prompt
    """
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    """
    This will display the main page
    """
    if authenticated_userid(request) is None:
        raise HTTPForbidden()
    return {"sources":sources.keys(), "hashtypes":hashtypes, 
        "instance_types":list(map(
            lambda x: {"instance_type":x[0], "type_name":x[1][0]}, 
            instance_types.items()))}

@view_config(route_name='getinfo', renderer='json')
def get_info_view(request):
    """
    This page is designed to be called by an Ajax request and return all
    information for the interface
    """
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    if "instance_type" in request.params:
        instance_type = request.params["instance_type"]
        spotprice = get_spot_price(instance_type)
    else:
        spotprice = "0"
        
    return {"hashes":list(map(lambda x: x.to_dict(), hashes.values())),
        "machines":list(map(lambda x: x.to_dict(), machines.values())), 
        "spotprice":spotprice}

@view_config(route_name='cancelhash')
def cancel_hash_view(request):
    """
    Remove the given hash from our hashlist
    """
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    if "hash" in request.params:
        remove_hash(request.params["hash"])
        return Response()
    else:
        return HTTPBadRequest()

@view_config(route_name='newmachines')
def request_new_machine_view(request):
    """
    Request new amazon instances
    """
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    try:
        is_spot = request.params["spot"] == "true"
        number = int(request.params["number"])
        instance_type = request.params["instance_type"]
    except KeyError:
        return HTTPBadRequest()

    if "price" in request.params:
        price = float(request.params["price"])
    else:
        price = None

    new_instances(number, is_spot, price, instance_type)

    return Response()

@view_config(route_name='killmachine')
def kill_machine_view(request):
    """
    Terminate the given machine
    """
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    try:
        uuid = request.params["uuid"]
    except KeyError:
        return HTTPBadRequest()

    kill_instance(uuid)
    return Response()

@view_config(route_name='submithash')
def submithash_view(request):
    """
    Submit a new hash to be cracked
    """
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    try:
        hashstring = request.params['hash']
        hashtype = request.params['hash_type'] 
        sourcename = request.params['source']
    except KeyError: 
        return HTTPBadRequest()

    hash_ = HashTracker(hashstring, hashtype, sources[sourcename])
    add_hash(hash_)
    return Response()

#
# The following functions are designed to be called by clients
#

@view_config(route_name='getworkshare', renderer='json')
def get_workshare_view(request):
    """
    Get a new workshare for the requesting client
    """
    # If a valid uuid isn't included then fail
    try:
        uuid = request.params['uuid']
        machine = machines[uuid]
    except KeyError:
        return HTTPForbidden()

    # Register a contact from the client
    machine.ipaddr = request.client_addr
    machine.contact()

    # If the client didn't request a size, default to 30k
    try:
        size = request.params['size']
    except KeyError:
        size = 30000 
    share = get_workshare(int(size))
    if share is not None:
        machine.add_workshare(share)
        return share.to_dict()
    else:
        # If we don't have a share, then just sleep for 10 seconds
        return {"sleep":10}

@view_config(route_name='completeworkshare')
def complete_workshare_view(request):
    """
    Set workshare as complete
    """
    # Fail if no valid UUID is provided
    try:
        uuid = request.params['uuid']
        machine = machines[uuid]
    except KeyError:
        return HTTPForbidden()

    try:
        hash_string = request.params['hash']
        workshare_start = int(request.params['start'])
        num_hashes = int(request.params['num_hashes'].split(' ')[0])
        size = int(request.params['size'])
    except KeyError:
        return HTTPBadRequest()

    # If we found a password, set the hash as complete
    if 'password' in request.params and hash_string in hashes:
        hashes[hash_string].complete_hash(request.params['password']) 

    complete_workshare(hash_string, size)
        
    machine.contact()
    machine.complete_workshare(hash_string, workshare_start, num_hashes)
    return Response()
