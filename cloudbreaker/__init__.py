from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('root', '/')
    config.add_route('gethashes', '/hashes')
    config.add_route('submithash', '/submit')
    config.scan()
    return config.make_wsgi_app()
