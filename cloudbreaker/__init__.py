from pyramid.config import Configurator
from .machines import machines, Machine
from .hashmanager import PasswordSource,sources


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('root', '/')
    config.add_route('gethashes', '/hashes')
    config.add_route('submithash', '/submit')
    config.add_route('getmachines', '/machines')
    config.add_route('getworkshare', '/getshare')
    config.add_route('completeworkshare', '/completeshare')
    config.scan()

    sources['dictionary'] = PasswordSource('dictionary', 50000)

    testmachine = Machine()
    testmachine.ipaddr = "127.0.0.1"
    machines[testmachine.uuid] = testmachine
    testmachine.contact()

    return config.make_wsgi_app()
