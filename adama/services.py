from base64 import b64encode
import textwrap

from flask import g
from flask.ext import restful
from werkzeug.datastructures import FileStorage

from .requestparser import RequestParser
from .tools import namespace_of
from .service import (ServiceModel, register_code, Service,
                      start_registration,
                      register_git_repository, post_notifier)
from .stores import namespace_store, service_store
from .api import APIException, ok, api_url_for
from .swagger import swagger
from .entity import get_permissions
from .command.tools import service
from .namespace import Namespace


class ServicesResource(restful.Resource):

    def post(self, namespace):
        """Create new service"""

        if namespace not in namespace_store:
            raise APIException(
                "namespace not found: {}".format(namespace), 404)

        ns = Namespace.from_json(namespace_store[namespace])
        if 'POST' not in get_permissions(ns.users, g.user):
            raise APIException(
                'user {} does not have permissions to POST to '
                'namespace {}'.format(g.user, namespace))

        args = self.validate_post()
        args['namespace'] = namespace
        reg_id = start_registration(args)
        return ok({
            'message': 'registration started',
            'state': api_url_for(
                'registration_state',
                namespace=namespace,
                reg_id=reg_id)
        })

    @staticmethod
    def validate_post():
        parser = RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('version', type=str, required=True)
        parser.add_argument('notify', type=str, required=False,
                            default='')
        parser.add_argument('code', type=FileStorage, location='files',
                            required=False)
        parser.add_argument('git_repository', type=str, required=False,
                            default=''),
        parser.add_argument('git_branch', type=str, required=False,
                            default='master'),
        parser.add_argument('metadata_path', type=str, required=False,
                            default='')

        args = parser.parse_args()

        for key, value in args.items():
            if value is None:
                del args[key]

        if 'code' in args and args['git_repository']:
            raise APIException(
                'cannot have code and git repository at '
                'the same time')

        if 'code' in args:
            filename = args.code.filename
            code = args.code.stream.read()
            args['code_content'] = b64encode(code)
            args['code_filename'] = filename

        try:
            args['user'] = g.user
        except RuntimeError:
            args['user'] = 'anonymous'
            
        return args

    def get(self, namespace):
        """List all services"""

        if namespace not in namespace_store:
            raise APIException(
                "namespace not found: {}".format(namespace), 404)

        result = [srv
                  for name, srv in service_store.items()
                  if namespace_of(name) == namespace]
        return ok({'result': result})


def all_services():
    """A generator returning all services.

    :rtype: Generator[Service]

    """
    for name in service_store:
        try:
            yield service(name)
        except KeyError:
            pass


