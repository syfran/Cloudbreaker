from pyramid.view import view_config

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    return {}
