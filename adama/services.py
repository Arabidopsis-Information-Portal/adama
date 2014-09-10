import urlparse

from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse
from werkzeug.datastructures import FileStorage

from .store import Store
from .tools import RequestParser
from .service import Service, identifier
from .namespaces import namespace_store
from .api import APIException


class ServicesStore(Store):

    def __init__(self):
        # Use Redis db=2 for services
        super(ServicesStore, self).__init__(db=2)


class Services(restful.Resource):

    def post(self, namespace):
        """Create new service"""

        if not namespace in namespace_store:
            raise APIException(
                "unknown namespace '{}'".format(namespace), 400)

        args = self.validate_post()
        iden = identifier(**args)
        full_name = full_identifier(namespace, iden)
        if full_name in service_store:
            raise APIException("service '{}' already exists in namespace {}"
                               .format(iden, namespace), 400)

        service = Service(**args)
        service_store[full_name] = service
        return {
            'status': 'success',
            'result': urlparse.urljoin(
                Config.get('server', 'url'), namespace, iden)
        }

    def validate_post(self):
        parser = RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='name of service is required')
        parser.add_argument('version', type=str, default='0.1')
        parser.add_argument('url', type=str, required=True,
                            help='url of data source is required')
        parser.add_argument('whitelist', type=str, action='append',
                            default=[])
        parser.add_argument('description', type=str, default='')
        parser.add_argument('requirements', type=str, action='append',
                            default=[])
        parser.add_argument('notify', type=str, default='')
        parser.add_argument('code', type=FileStorage, required=True,
                            location='files',
                            help='a file, tarball, or zip, must be uploaded')

        args = parser.parse_args()
        args.adapter = args.code.filename
        args.code = args.code.stream.read()

        return args

    def get(self, namespace):
        """List all services"""

        result = {srv.iden: srv.to_json()
                  for name, srv in service_store.items()
                  if namespace_of(name) == namespace}
        return {
            'status': 'success',
            'result': result
        }


def full_identifier(namespace, identifier):
    return '{}.{}'.format(namespace, identifier)


def namespace_of(full_identifier):
    return full_identifier.split('.')[0]


service_store = ServicesStore()