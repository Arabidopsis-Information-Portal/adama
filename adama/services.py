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


TARBALLS = ['.tar', '.gz', '.tgz']
ZIPS = ['.zip']

EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.rb': 'ruby',
    '.jar': 'java',
    '.lua': 'lua'
}


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

    @staticmethod
    def validate_post():
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


def register_code(args, namespace):
    pass


def register_git_repository(args, namespace):
    pass


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


def extract(filename, code, into):
    """Extract code from string ``code``.

    ``filename`` is the name of the uploaded file.  Extract the code
    in directory ``into``.

    Return the directory where the user code is extracted (may differ from
    the original ``into``).

    """

    ext = os.path.splitext(filename)
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


