from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from hashmanager import add_hash, HashTracker, hashes
from passwordsource import sources

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    return {}

@view_config(route_name='gethashes', renderer='json')
def get_hashes(request):
    return map(lambda x: x.toDict(), hashes.values())

@view_config(route_name='submithash')
def submithash(request):
    try:
        hashstring = request.params['hash']
        hashtype = request.params['type'] 
        sourcename = request.params['source']
    except KeyError: 
        return HTTPBadRequest()
    hash_ = HashTracker(hashstring, hashtype, sources[sourcename])
    add_hash(hash_)
    return Response()
