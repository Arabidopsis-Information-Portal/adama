from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse
from werkzeug.datastructures import FileStorage

from .store import Store
from .tools import RequestParser


class ServicesStore(Store):

    def __init__(self):
        # Use Redis db=2 for services
        super(ServicesStore, self).__init__(db=2)


class Services(restful.Resource):

    def post(self, namespace):
        """Create new service"""

        args = self.validate_post()
        print(args)
        return {}

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
        args.code = args.code.stream

        return args

    def get(self, namespace):
        """List all services"""
        pass