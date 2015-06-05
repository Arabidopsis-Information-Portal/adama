import base64
import os

from flask import render_template, request, abort, send_from_directory, g
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
                      ServiceListResource, ServiceHealthResource,
                      IconResource, StatsResource)
from .passthrough import PassthroughServiceResource
from .servicedocs import ServiceDocsResource, ServiceDocsUIResource
from .status import StatusResource
from .stores import token_store
from .tools import location_of, get_token
from .provenance import ProvResource


PREFIX = Config.get('server', 'prefix')
HERE = location_of(__file__)

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
api.add_resource(ServiceHealthResource,
                 url('/<string:namespace>/<string:service>/_health'),
                 endpoint='health')
api.add_resource(ServiceDocsResource,
                 url('/<string:namespace>/<string:service>/docs'),
                 endpoint='service_docs')
api.add_resource(ServiceDocsUIResource,
                 url('/<string:namespace>/<string:service>/docs/swagger'),
                 endpoint='service_swagger')
api.add_resource(ProvResource,
                 url('/<string:namespace>/<string:service>/prov'),
                 url('/<string:namespace>/<string:service>/'
                     'prov/<string:uuid>'),
                 endpoint='prov')
api.add_resource(IconResource,
                 url('/<string:namespace>/<string:service>/icon'),
                 endpoint='service_icon')
api.add_resource(StatsResource,
                 url('/<string:namespace>/<string:service>/stats'),
                 endpoint='stats')


@app.route('/home')
def home():
    return render_template('template.html')


@app.route('/api/adama/swagger-ui.js')
def swagger_ui():
    return app.send_static_file('js/swagger-ui.js')


@app.route('/docs/<path:path>')
def docs_adapters(path):
    return send_from_directory(
        os.path.join(HERE, 'static/html/'), path)


def is_docs_endpoint(req):
    """

    :type req: Request
    :rtype: bool
    """
    return req.path.endswith('/docs') or req.path.endswith('/docs/swagger')


@app.before_request
def check_access():
    # allow unrestricted access to docs
    if (request.path.startswith('/api/adama') or
            request.path.startswith('/docs') or
            request.path.startswith('/swagger-ui') or
            is_docs_endpoint(request)):
        return
    # don't control access to OPTIONS verb
    if request.method == 'OPTIONS':
        return
    access_control_type = Config.get('server', 'access_control')
    if access_control_type == 'none':
        g.user = 'anonymous'
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


def check_jwt(req):
    tenant_name = Config.get('server', 'tenant_name')
    try:
        decoded = jwt.decode(
            req.headers['X-JWT-Assertion-{0}'.format(tenant_name)],
            PUB_KEY)
        g.user = decoded['http://wso2.org/claims/enduser']
    except (jwt.DecodeError, KeyError):
        abort(400)


def check_bearer_token(req):
    # --- REVIEW THIS ---
    # Allow unauthorized GET requests for now
    if req.method == 'GET':
        return
    # ------
    # bypass auth in /json and non-prefixed urls
    if req.path == PREFIX + '/json':
        return
    if not req.path.startswith(PREFIX):
        return
    token = get_token(req.headers)
    if token is None:
        abort(400)
    try:
        g.user = token_store[token]
        app.logger.debug('user {}'.format(g.user))
    except KeyError:
        abort(400)


@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
