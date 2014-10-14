import re

from flask import render_template, redirect, url_for, request, abort

from . import app
from .api import api
from .config import Config
from .namespaces import NamespacesResource
from .namespace import NamespaceResource
from .services import ServicesResource
from .service import (ServiceResource, ServiceQueryResource,
                      ServiceListResource)
from .status import StatusResource
from .token_store import token_store

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


TOKEN_RE = re.compile('Bearer (.+)')

@app.before_request
def check_token():
    if not Config.getboolean('server', 'auth'):
        return
    # --- REVIEW THIS ---
    # Allow unauthorized GET requests for now
    if request.method == 'GET':
        return
    # ------
    # bypass auth in /json and non-prefixed urls
    if request.path == PREFIX + '/json':
        return
    if not request.path.startswith(PREFIX):
        return
    auth = request.headers['Authorization']
    match = TOKEN_RE.match(auth)
    if not match:
        abort(400)
    token = match.group(1)
    if token not in token_store:
        abort(400)
