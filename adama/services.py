from flask import request
from flask.ext import restful
from flask.ext.restful import reqparse

from .store import Store


class ServicesStore(Store):

    def __init__(self):
        # Use Redis db=2 for services
        super(ServicesStore, self).__init__(db=2)


class Services(restful.Resource):

    def post(self, namespace):
        """Create new service"""
        pass

    def get(self, namespace):
        """List all services"""
        pass