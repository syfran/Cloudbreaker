import os

from pyramid.config import Configurator
from .machines import machines, Machine
from .hashmanager import PasswordSource,sources
from .amazon import init_boto

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

def check_env_auth(username, password, request):
    if 'CLOUDBREAKER_HTTP_PASS' not in os.environ:
        return None 
    if username == "cloudbreaker" and password == os.environ['CLOUDBREAKER_HTTP_PASS']:
        
        return []
    return None

    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.set_authentication_policy(BasicAuthAuthenticationPolicy(check_env_auth))
    config.set_authorization_policy(ACLAuthorizationPolicy())

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('root', '/')
    config.add_route('gethashes', '/hashes')
    config.add_route('submithash', '/submit')
    config.add_route('getmachines', '/machines')
    config.add_route('getworkshare', '/getshare')
    config.add_route('completeworkshare', '/completeshare')
    config.add_route('getspotprice', '/spotprice')
    config.scan()

    init_boto()

    sources['dictionary'] = PasswordSource('dictionary', 50000)

    testmachine = Machine()
    testmachine.uuid = "abcd"
    machines[testmachine.uuid] = testmachine

    return config.make_wsgi_app()
