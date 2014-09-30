import json
import multiprocessing
import os
import tarfile
import tempfile
import re
import zipfile

from flask import url_for
from flask.ext import restful
from werkzeug.datastructures import FileStorage
import requests

from . import app
from .service_store import service_store
from .requestparser import RequestParser
from .tools import namespace_of, adapter_iden
from .service import Service, identifier, EXTENSIONS
from .namespaces import namespace_store
from .api import APIException, ok, error


TARBALLS = ['.tar', '.gz', '.tgz']
ZIPS = ['.zip']


class ServicesResource(restful.Resource):

    def post(self, namespace):
        """Create new service"""

        if namespace not in namespace_store:
            raise APIException(
                "namespace not found: {}".format(namespace), 404)

        args = self.validate_post()
        if args.code and args.git_repository:
            raise APIException(
                'cannot have code and git repository at '
                'the same time')

        if args.code:
            return register_code(args, namespace)

        if args.git_repository:
            return register_git_repository(args, namespace)

    @staticmethod
    def validate_post():
        parser = RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('type', type=str)
        parser.add_argument('version', type=str)
        parser.add_argument('url', type=str)
        parser.add_argument('whitelist', type=str, action='append')
        parser.add_argument('description', type=str)
        parser.add_argument('requirements', type=str, action='append')
        parser.add_argument('notify', type=str)
        parser.add_argument('json_path', type=str)
        parser.add_argument('main_module', type=str)
        # The following two options are exclusive
        parser.add_argument('code', type=FileStorage, location='files')
        parser.add_argument('git_repository', type=str)

        args = parser.parse_args()

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


def register_code(args, namespace):
    filename = args.code.filename
    code = args.code.stream.read()
    tempdir = tempfile.mkdtemp()
    user_code = extract(filename, code, tempdir)
    return register(args, namespace, user_code)


def register_git_repository(args, namespace):
    # check out code
    # call register (args, namespace, checkout)
    pass


def register(args, namespace, user_code):
    """Register a service in a namespace.

    ``args`` is a dictionary with POST parameters. ``user_code`` is the
    directory where the user's code is checked out.

    Create the proper image, launch workers, and save the service in
    the store.

    """
    service = Service(namespace=namespace, code_dir=user_code, **dict(args))
    try:
        slot = service_store[service.iden]['slot']
    except KeyError:
        slot = 'free'

    # make sure to only use free or errored out slots
    if slot not in ('free', 'error'):
        raise APIException("service slot not available: {}\n"
                           "Current state: {}"
                           .format(service.iden, slot), 400)

    service_store[service.iden] = {
        'slot': 'busy',
        'msg': 'Empty service created',
        'stage': 1,
        'total_stages': 5,
        'service': None
    }

    _async_register(service)
    return ok({
        'message': 'registration started',
        'result': {
            'state_url': url_for(
                'service',
                namespace=service.namespace,
                service=service.adapter_name,
                _external=True),
            'search_url': url_for(
                'search',
                namespace=service.namespace,
                service=service.adapter_name,
                _external=True),
            'list_url': url_for(
                'list',
                namespace=service.namespace,
                service=service.adapter_name,
                _external=True),
            'notification': service.notify
        }
    })


def _async_register(service):
    proc = multiprocessing.Process(
        name='Async Registration {}'.format(service.iden),
        target=_register, args=(service,))
    proc.start()


def _register(service):
    full_name = service.iden
    slot = service_store[full_name]
    try:
        slot['msg'] = 'Async image creation started'
        slot['stage'] = 2
        service_store[full_name] = slot

        service.make_image()

        slot['msg'] = 'Image for service created'
        slot['stage'] = 3
        service_store[full_name] = slot

        service.start_workers()

        slot['msg'] = 'Workers started'
        slot['stage'] = 4
        service_store[full_name] = slot

        service.check_health()

        slot['msg'] = 'Service ready'
        slot['stage'] = 5
        slot['slot'] = 'ready'
        slot['service'] = service
        service_store[full_name] = slot

        data = ok({
            'result': {
                'service': url_for('service',
                                   namespace=service.namespace,
                                   service=service.adapter_name,
                                   _external=True)
            }
        })
    except Exception as exc:
        slot['msg'] = 'Error: {}'.format(exc)
        slot['slot'] = 'error'
        service_store[full_name] = slot
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


def extract(filename, code, into):
    """Extract code from string ``code``.

    ``filename`` is the name of the uploaded file.  Extract the code
    in directory ``into``.

    Return the directory where the user code is extracted (may differ from
    the original ``into``).

    """

    _, ext = os.path.splitext(filename)
    user_code_dir = os.path.join(into, 'user_code')
    os.mkdir(user_code_dir)
    contents = code

    if ext in ZIPS:
        # it's a zip file
        zip_file = os.path.join(into, 'contents.zip')
        with open(zip_file, 'w') as f:
            f.write(contents)
        zip = zipfile.ZipFile(zip_file)
        zip.extractall(user_code_dir)

    elif ext in TARBALLS:
        # it's a tarball
        tarball = os.path.join(into, 'contents.tgz')
        with open(tarball, 'w') as f:
            f.write(contents)
        tar = tarfile.open(tarball)
        tar.extractall(user_code_dir)

    elif ext in EXTENSIONS.keys():
        # it's a module
        module = os.path.join(user_code_dir, filename)
        with open(module, 'w') as f:
            f.write(contents)

    else:
        raise APIException(
            'unknown extension: {0}'.format(filename), 400)

    return user_code_dir


