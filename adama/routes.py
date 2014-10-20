import base64
import re

from flask import render_template, redirect, url_for, request, abort
from Crypto.PublicKey import RSA
import jwt

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


@app.before_request
def check_access():
    # don't control access to OPTIONS verb
    if request.method == 'OPTIONS':
        return
    access_control_type = Config.get('server', 'access_control')
    if access_control_type == 'none':
        return
    if access_control_type == 'jwt':
        return check_jwt(request)
    if access_control_type == 'bearer_token':
        return check_bearer_token(request)
    abort(400)


def get_pub_key():
    pub_key = Config.get('server', 'apim_public_key')
    return RSA.importKey(base64.b64decode(pub_key))


PUB_KEY = get_pub_key()

def check_jwt(request):
    tenant_name = Config.get('server', 'tenant_name')
    try:
        decoded = jwt.decode(
            request.headers['X-JWT-Assertion-{0}'.format(tenant_name)],
            PUB_KEY)
    except (jwt.DecodeError, KeyError):
        abort(400)


TOKEN_RE = re.compile('Bearer (.+)')

def check_bearer_token(request):
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

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

