import json
import multiprocessing

from flask import url_for
from flask.ext import restful
from werkzeug.datastructures import FileStorage
import requests

from . import app
from .service_store import service_store
from .tools import RequestParser, namespace_of
from .service import Service, identifier
from .namespaces import namespace_store
from .api import APIException


class ServicesResource(restful.Resource):

    def post(self, namespace):
        """Create new service"""

        if namespace not in namespace_store:
            raise APIException(
                "unknown namespace '{}'".format(namespace), 400)

        args = self.validate_post()
        iden = identifier(namespace=namespace, **args)
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
        state_url = url_for('service', namespace=namespace, service=iden,
                            _external=True)
        search_url = url_for('search', namespace=namespace, service=iden,
                             _external=True)
        return {
            'status': 'success',
            'message': 'registration started',
            'result': {
                'state': state_url,
                'search': search_url,
                'notification': service.notify
            }
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
        parser.add_argument('type', type=str, default='QueryWorker')
        parser.add_argument('json_path', type=str, default='')
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
        data = {
            'status': 'success',
            'result': {
                'service': url_for('service',
                                   namespace=namespace, service=service.iden,
                                   _external=True),
                'search': url_for('search',
                                  namespace=namespace, service=service.iden,
                                  _external=True)
            }
        }
    except Exception as exc:
        service_store[full_name] = 'Error: {}'.format(exc)
        data = {
            'status': 'error',
            'result': str(exc)
        }
    if service.notify:
        try:
            requests.post(service.notify,
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data))
        except Exception:
            app.logger.warning(
                "Could not notify url '{}' that '{}' is ready"
                .format(service.notify, full_name))
