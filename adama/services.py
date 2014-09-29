import json
import multiprocessing
import re

from flask import url_for
from flask.ext import restful
from werkzeug.datastructures import FileStorage
import requests

from . import app
from .service_store import service_store
from .requestparser import RequestParser
from .tools import namespace_of, adapter_iden
from .service import Service, identifier
from .namespaces import namespace_store
from .api import APIException, ok, error


class ServicesResource(restful.Resource):

    def post(self, namespace):
        """Create new service"""

        if namespace not in namespace_store:
            raise APIException(
                "namespace not found: {}".format(namespace), 404)

        args = self.validate_post()
        iden = identifier(namespace, args.name, args.version)
        adapter_name = adapter_iden(**args)
        if iden in service_store and \
           not isinstance(service_store[iden], basestring):
            raise APIException("service '{}' already exists"
                               .format(iden), 400)

        service = Service(namespace=namespace, **args)
        service_store[iden] = '[1/5] Empty service created'
        proc = multiprocessing.Process(
            name='Async Register {}'.format(iden),
            target=register, args=(namespace, service))
        proc.start()
        state_url = url_for(
            'service', namespace=namespace, service=adapter_name,
            _external=True)
        search_url = url_for(
            'search', namespace=namespace, service=adapter_name,
            _external=True)
        return ok({
            'message': 'registration started',
            'result': {
                'state': state_url,
                'search': search_url,
                'notification': service.notify
            }
        })

    def validate_post(self):
        parser = RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='name of service is required')
        parser.add_argument('type', type=str,
                            default='query')
        parser.add_argument('version', type=str,
                            default='0.1')
        parser.add_argument('url', type=str,
                            default='http://localhost')
        parser.add_argument('whitelist', type=str, action='append',
                            default=[])
        parser.add_argument('description', type=str,
                            default='')
        parser.add_argument('requirements', type=str, action='append',
                            default=[])
        parser.add_argument('notify', type=str,
                            default='')
        parser.add_argument('json_path', type=str,
                            default='')
        parser.add_argument('main_module', type=str,
                            default='main')
        # The following two options are exclusive
        parser.add_argument('code', type=FileStorage, location='files')
        parser.add_argument('git_repository', type=str)

        args = parser.parse_args()
        args.adapter = args.code.filename
        args.code = args.code.stream.read()

        if not valid_image_name(args.name):
            raise APIException("'{}' is not a valid service name.\n"
                               "Allowed characters: [a-z0-9_.-]"
                               .format(args.name))

        return args

    def get(self, namespace):
        """List all services"""

        result = [srv.to_json()
                  for name, srv in service_store.items()
                  if namespace_of(name) == namespace and
                  not isinstance(srv, basestring)]
        return ok({'result': result})


def valid_image_name(name):
    return re.search(r'[^a-z0-9-_.]', name) is None


def register(namespace, service):
    """Register a service in a namespace.

    Create the proper image, launch workers, and save the service in
    the store.

    """
    try:
        full_name = service.iden
        service_store[full_name] = '[2/5] Async image creation started'
        service.make_image()
        service_store[full_name] = '[3/5] Image for service created'
        service.start_workers()
        service_store[full_name] = '[4/5] Workers started'
        service.check_health()
        service_store[full_name] = service
        data = ok({
            'result': {
                'service': url_for('service',
                                   namespace=namespace, service=service.iden,
                                   _external=True),
                'search': url_for('search',
                                  namespace=namespace, service=service.iden,
                                  _external=True)
            }
        })
    except Exception as exc:
        service_store[full_name] = 'Error: {}'.format(exc)
        data = error({'result': str(exc)})
    if service.notify:
        try:
            requests.post(service.notify,
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data))
        except Exception:
            app.logger.warning(
                "Could not notify url '{}' that '{}' is ready"
                .format(service.notify, full_name))
