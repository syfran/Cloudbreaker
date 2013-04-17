from pyramid.view import view_config


@view_config(route_name='projectView', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'cloudbreaker'}

@view_config(route_name='root', renderer='templates/root_template.pt')
def root_view(request):
    return {}
