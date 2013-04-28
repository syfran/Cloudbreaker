from pyramid.view import view_config
from pyramid.httpexceptions import *
from pyramid.response import Response
from pyramid.security import forget, authenticated_userid

from .hashmanager import *
from .machines import machines
from .amazon import *

@view_config(context=HTTPForbidden)
def auth_test(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    if authenticated_userid(request) is None:
        raise HTTPForbidden()
    return {"sources":sources.keys(), "hashtypes":hashtypes}

@view_config(route_name='getinfo', renderer='json')
def get_hashes_view(request):
    if authenticated_userid(request) is None:
        raise HTTPForbidden()
    return {"hashes":list(map(lambda x: x.to_dict(), hashes.values())),
        "machines":list(map(lambda x: x.to_dict(), machines.values())), 
        "spotprice":get_spot_price()}

@view_config(route_name='cancelhash')
def cancel_hash_view(request):
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    if "hash" in request.params:
        remove_hash(request.params["hash"])
        return Response()
    else:
        return HTTPBadRequest()

@view_config(route_name='newmachines')
def request_new_machine_view(request):
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    if "spot" in request.params:
        is_spot = request.params["spot"]
    else: 
        is_spot = True

    if "price" in request.params:
        price = float(request.params["price"])
    else:
        price = None

    if "number" in request.params:
        number = int(request.params["number"])
    else:
        number = 1

    new_instances(number, is_spot, price) 

    return Response()

@view_config(route_name='killmachine')
def kill_machine_view(request):
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    try:
        uuid = request.params["uuid"]
    except KeyError:
        return HTTPBadRequest()

    kill_instance(uuid)
    return Response()

@view_config(route_name='getworkshare', renderer='json')
def get_workshare_view(request):
    try:
        uuid = request.params['uuid']
        machine = machines[uuid]
    except KeyError:
        return HTTPForbidden()

    machine.ipaddr = request.client_addr
    machine.contact()
    try:
        size = request.params['size']
    except KeyError:
        size = 30000 
    share = get_workshare(int(size))
    if share is not None:
        machine.add_workshare(share)
        return share.to_dict()
    else:
        return {"sleep":10}

@view_config(route_name='completeworkshare')
def complete_workshare_view(request):
    try:
        uuid = request.params['uuid']
        machine = machines[uuid]
    except KeyError:
        return HTTPForbidden()

    try:
        hash_string = request.params['hash']
        workshare_start = request.params['start']
        num_hashes = request.params['num_hashes']
        size = request.params['size']
    except KeyError:
        return HTTPBadRequest()

    if 'password' in request.params and hash_string in hashes:
        hashes[hash_string].complete_hash(request.params['password']) 

    complete_workshare(hash_string, size)
        
    machine.contact()
    machine.complete_workshare(hash_string, workshare_start, num_hashes)
    return Response()

@view_config(route_name='submithash')
def submithash_view(request):
    if authenticated_userid(request) is None:
        raise HTTPForbidden()

    try:
        hashstring = request.params['hash']
        hashtype = request.params['type'] 
        sourcename = request.params['source']
    except KeyError: 
        return HTTPBadRequest()
    hash_ = HashTracker(hashstring, hashtype, sources[sourcename])
    add_hash(hash_)
    return Response()
