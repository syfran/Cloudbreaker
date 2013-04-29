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
    config.add_route('getinfo', '/ajaxinfo')
    config.add_route('submithash', '/submit')
    config.add_route('cancelhash', '/cancelhash')
    config.add_route('killmachine', '/killmachine')
    config.add_route('newmachines', '/newmachines')
    config.add_route('getworkshare', '/getshare')
    config.add_route('completeworkshare', '/completeshare')
    config.scan()

    init_boto()

    sources['ruledict'] = PasswordSource('ruledict', "Dictionary with jtr rule mangling", 306706)

    # For testing instances
    # remove for any production
    mach = Machine()
    mach.uuid = "abcd"
    machines[mach.uuid] = mach

    return config.make_wsgi_app()
