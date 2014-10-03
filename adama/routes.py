from flask import render_template, redirect, url_for

from . import app
from .api import api
from .config import Config
from .namespaces import NamespacesResource
from .namespace import NamespaceResource
from .services import ServicesResource
from .service import (ServiceResource, ServiceQueryResource,
                      ServiceListResource)
from .status import StatusResource


PREFIX = Config.get('server', 'prefix')


print('Using PREFIX = {}'.format(PREFIX))


def url(endpoint):
    return PREFIX + endpoint


api.add_resource(NamespacesResource, url('/namespaces'),
                 endpoint='namespaces')
api.add_resource(StatusResource, url('/status'))
api.add_resource(NamespaceResource, url('/<string:namespace>'),
                 endpoint='namespace')
api.add_resource(ServicesResource, url('/<string:namespace>/services'))
api.add_resource(ServiceResource, url('/<string:namespace>/<string:service>'),
                 endpoint='service')
api.add_resource(ServiceQueryResource,
                 url('/<string:namespace>/<string:service>/search'),
                 endpoint='search')
api.add_resource(ServiceListResource,
                 url('/<string:namespace>/<string:service>/list'),
                 endpoint='list')


@app.route('/home')
def hello_world():
    return render_template('template.html')


@app.route('/')
def root():
    return redirect(url_for('hello_world'))