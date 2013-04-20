from pyramid.view import view_config

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    return {}

@view_config(route_name='gethashes', renderer='json')
def get_hashes(request):
    return {}

@view_config(route_name='submithash')
def submithash(request):
    hashstring = request.params['hash']
    hashtype = request.params['type'] 
    source = request.params['source']
    hash_ = HashTracker(hashstring, hashtype, source)
    add_hash(hash_)
    return Response("200 - OK")
