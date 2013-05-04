"""
This module initializes the pyramid app
"""
import os

from pyramid.config import Configurator
from .machines import machines, Machine
from .hashmanager import PasswordSource,sources
from .amazon import init_boto

from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

def check_env_auth(username, password, request):
    """
    Check a username and password from basic auth.
    Username should be cloudbreaker and the password in the
    "CLOUDBREAKER_HTTP_PASS variable
    """
    if 'CLOUDBREAKER_HTTP_PASS' not in os.environ:
        return None 
    if username == "cloudbreaker" and password == os.environ['CLOUDBREAKER_HTTP_PASS']:
        return []
    return None

def main(global_config, **settings):
    """ 
    This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    # Add our basic HTTP auth policy
    config.set_authentication_policy(BasicAuthAuthenticationPolicy(check_env_auth))
    config.set_authorization_policy(ACLAuthorizationPolicy())

    config.add_static_view('static', 'static', cache_max_age=3600)
    # Add all our outes
    config.add_route('root', '/')
    config.add_route('getinfo', '/ajaxinfo')
    config.add_route('submithash', '/submit')
    config.add_route('cancelhash', '/cancelhash')
    config.add_route('killmachine', '/killmachine')
    config.add_route('newmachines', '/newmachines')
    config.add_route('getworkshare', '/getshare')
    config.add_route('completeworkshare', '/completeshare')
    config.scan()

    # Initialize our Amazon AWS connection
    init_boto()

    # Addo our dictionary
    sources['ruledict'] = PasswordSource('ruledict', "Dictionary with jtr rule mangling", 306706)

    # For testing instances
    # remove for any production
    #mach = Machine("t1.micro")
    #mach.uuid = "abcd"
    #mach.is_spot = True
    #machines[mach.uuid] = mach

    return config.make_wsgi_app()
