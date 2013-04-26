from pyramid.view import view_config
from pyramid.httpexceptions import *
from pyramid.response import Response

from .hashmanager import *
from .machines import machines

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    return {"sources":sources.keys(), "hashtypes":hashtypes}

@view_config(route_name='gethashes', renderer='json')
def get_hashes_view(request):
    return list( map(lambda x: x.to_dict(), hashes.values()))

@view_config(route_name='getmachines', renderer='json')
def get_machines(request):
    return list(map(lambda x: x.to_dict(), machines.values()))


@view_config(route_name='getworkshare', renderer='json')
def get_workshare_view(request):
    try:
        uuid = request.params['uuid']
        machine = machines[uuid]
    except KeyError:
        return HTTPForbidden()

    machine.contact()
    try:
        size = request.params['size']
    except KeyError:
        size = 30000 
    share = get_workshare(int(size))
    machine.add_workshare(share)
    if share is not None:
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
    except KeyError:
        return HTTPBadRequest()

    if password in request.params:
        hashes["hash_string"].password = password 
        
    machine.contact()
    machine.complete_workshare(hash_string, workshare_start)
    return Response()

@view_config(route_name='submithash')
def submithash_view(request):
    try:
        hashstring = request.params['hash']
        hashtype = request.params['type'] 
        sourcename = request.params['source']
    except KeyError: 
        return HTTPBadRequest()
    hash_ = HashTracker(hashstring, hashtype, sources[sourcename])
    add_hash(hash_)
    return Response()
