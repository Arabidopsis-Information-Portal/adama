import textwrap

from flask import g
from flask.ext import restful
from werkzeug.datastructures import FileStorage

from .requestparser import RequestParser
from .tools import namespace_of
from .service import ServiceModel, start_registration
from .stores import namespace_store, service_store
from .api import APIException, ok, api_url_for
from .swagger import swagger
from .entity import get_permissions
from .command.tools import service


@swagger.model
@swagger.nested(
    result=ServiceModel.__name__
)
class ServicesResponseModel(object):

    resource_fields = {
        'status': restful.fields.String(attribute='success or error'),
        'result': restful.fields.List(
            restful.fields.Nested(ServiceModel.resource_fields))
    }


@swagger.model
class ServiceURLsModel(object):

    resource_fields = {
        'state_url': restful.fields.String(
            attribute='url to check state of registration'),
        'search_url': restful.fields.String(
            attribute='url to search endpoint of service'),
        'list_url': restful.fields.String(
            attribute='url to list endpoint of service'),
        'notification': restful.fields.String(
            attribute='url to notify when service is ready')
    }


@swagger.model
@swagger.nested(
    result=ServiceURLsModel.__name__
)
class CreatedServiceModel(object):

    resource_fields = {
        'status': restful.fields.String(attribute='success of error'),
        'message': restful.fields.String(attribute='registration started'),
        'result': restful.fields.Nested(ServiceURLsModel.resource_fields)
    }


class ServicesResource(restful.Resource):

    @swagger.operation(
        notes=textwrap.dedent(
            """Create a new service.

            <p> The preferred way to create a new service is by using a git
            repository with a metadata file 'metadata.yml'.  Use the
            parameter <b>git_repository</b> to specify a url from where to
            clone the repository. If the metadata file is not located at
            the root, then use the parameter <b>metadata</b> to point to
            it, relative to the root of the git repository.  All the other
            parameters can be specified in the metadata file.</p>

            <p> The parameters used as form values can be used to overwrite
            the values specified in the metadata file.<p>

            """),
        nickname='createService',
        responseClass=CreatedServiceModel.__name__,
        consumes='multipart/form-data',
        parameters=[
            {
                'name': 'namespace',
                'description': 'namespace of the service',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'path'
            },
            {
                'name': 'git_repository',
                'description': 'url of git repository',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'git_branch',
                'description': 'branch or tag to clone (default to "master")',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'metadata',
                'description': 'path of metadata file relative to '
                               'git_repository root',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'name',
                'description': 'name of the service',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'type',
                'description': 'type of the adapter',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'version',
                'description': 'version of the adapter',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'url',
                'description': 'url of the third party data service',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'whitelist',
                'description': 'ip or domain to be whitelisted',
                'required': False,
                'allowMultiple': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'description',
                'description': 'description of the service',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'requirements',
                'description': 'third party package needed by the adapter',
                'required': False,
                'allowMultiple': True,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'notify',
                'description': 'url to notify when adapter is ready',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'json_path',
                'description': 'location of the array of result in response',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'main_module',
                'description': 'path of main module relative to '
                               'git_repository root',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'icon',
                'description': 'path to an icon picture, relative to '
                               'the metadata.yml file (format: png)',
                'required': False,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'form'
            },
            {
                'name': 'code',
                'description': 'type of the adapter',
                'required': False,
                'allowMultiple': False,
                'dataType': 'File',
                'paramType': 'form'
            }
        ]
    )
    def post(self, namespace):
        """Create new service"""

        if namespace not in namespace_store:
            raise APIException(
                "namespace not found: {}".format(namespace), 404)

        ns = namespace_store[namespace]
        if 'POST' not in get_permissions(ns.users, g.user):
            raise APIException(
                'user {} does not have permissions to POST to '
                'namespace {}'.format(g.user, namespace))

        args = self.validate_post()
        if 'code' in args and 'git_repository' in args:
            raise APIException(
                'cannot have code and git repository at '
                'the same time')

        reg_id = start_registration(args, namespace)
        return ok({
            'message': 'registration started',
            'state': api_url_for(
                'registration_state',
                namespace=namespace,
                reg_id=reg_id)
        })

        # if 'code' in args or args.get('type') == 'passthrough':
        #     service = register_code(args, namespace, post_notifier)
        # elif 'git_repository' in args:
        #     service = register_git_repository(args, namespace, post_notifier)
        # else:
        #     raise APIException(
        #         'no code or git repository specified')
        #
        # result = {
        #     'state_url': api_url_for(
        #         'service',
        #         namespace=service.namespace,
        #         service=service.adapter_name),
        #     'notification': service.notify
        # }
        # for endpoint in service.endpoint_names():
        #     result[endpoint+'_url'] = api_url_for(
        #         endpoint,
        #         namespace=service.namespace,
        #         service=service.adapter_name)
        # return ok({
        #     'message': 'registration started',
        #     'result': result
        # })

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
        parser.add_argument('git_repository', type=str),
        parser.add_argument('git_branch', type=str),
        parser.add_argument('icon', type=str),
        parser.add_argument('validate_request', type=bool),
        parser.add_argument('metadata', type=str)

        args = parser.parse_args()

        for key, value in args.items():
            if value is None:
                del args[key]

        if 'code' in args:
            filename = args.code.filename
            code = args.code.stream.read()
            args['code'] = {
                'file': code,
                'filename': filename
            }
            
        return args

    @swagger.operation(
        notes='List all services registered in a given namespace.',
        nickname='getServices',
        responseClass=ServicesResponseModel.__name__,
        parameters=[
            {
                'name': 'namespace',
                'description': 'name of namespace',
                'required': True,
                'allowMultiple': False,
                'dataType': 'string',
                'paramType': 'path'
            }
        ]

    )
    def get(self, namespace):
        """List all services"""

        if namespace not in namespace_store:
            raise APIException(
                "namespace not found: {}".format(namespace), 404)

        result = [srv['service'].to_json()
                  for name, srv in service_store.items()
                  if namespace_of(name) == namespace and
                  srv['service'] is not None]
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


