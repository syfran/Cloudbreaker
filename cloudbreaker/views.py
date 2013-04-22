from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from .hashmanager import add_hash, HashTracker, hashes, get_workshare,sources
from .machines import machines

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    return {}

@view_config(route_name='gethashes', renderer='json')
def get_hashes_view(request):
    return list( map(lambda x: x.to_dict(), hashes.values()))

@view_config(route_name='getmachines', renderer='json')
def get_machines(request):
    return list(map(lambda x: x.to_dict(), machines.values()))


@view_config(route_name='getworkshare', renderer='json')
def get_workshare_view(request):
    share = get_workshare()
    if share is not None:
        return share.to_dict()
    else:
        return {"sleep":10}

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
