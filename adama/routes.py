import base64
import re

from flask import render_template, request, abort, url_for
from Crypto.PublicKey import RSA
import jwt

# monkey patch jwt to make it work with WSO2's algorithm
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
jwt.verify_methods['SHA256WITHRSA'] = (
    lambda msg, key, sig: PKCS1_v1_5.new(key).verify(SHA256.new(msg), sig))
jwt.prepare_key_methods['SHA256WITHRSA'] = jwt.prepare_RS_key

from . import app
from .api import api
from .config import Config
from .namespaces import NamespacesResource
from .namespace import NamespaceResource
from .services import ServicesResource
from .service import (ServiceResource, ServiceQueryResource,
                      ServiceListResource)
from .passthrough import PassthroughServiceResource
from .status import StatusResource
from .token_store import token_store

PREFIX = Config.get('server', 'prefix')


print('Using PREFIX = {}'.format(PREFIX))


def url(endpoint):
    return PREFIX + endpoint


api.add_resource(NamespacesResource, url('/namespaces'),
                 endpoint='namespaces')
api.add_resource(StatusResource, url('/status'),
                 endpoint='status')
api.add_resource(NamespaceResource, url('/<string:namespace>'),
                 endpoint='namespace')
api.add_resource(ServicesResource, url('/<string:namespace>/services'),
                 endpoint='services')
api.add_resource(ServiceResource, url('/<string:namespace>/<string:service>'),
                 endpoint='service')
api.add_resource(ServiceQueryResource,
                 url('/<string:namespace>/<string:service>/search'),
                 endpoint='search')
api.add_resource(ServiceListResource,
                 url('/<string:namespace>/<string:service>/list'),
                 endpoint='list')
api.add_resource(PassthroughServiceResource,
                 url('/<string:namespace>/<string:service>/access'),
                 url('/<string:namespace>/<string:service>/access/'
                     '<path:path>'),
                 endpoint='access')


@app.route('/home')
def home():
    return render_template('template.html')


@app.route('/api/adama/swagger-ui.js')
def swagger_ui():
    return app.send_static_file('js/swagger-ui.js')


@app.before_request
def check_access():
    # allow unrestricted access to docs
    if request.path.startswith('/api/adama'):
        return
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

