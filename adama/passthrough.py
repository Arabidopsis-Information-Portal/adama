from flask import request
from flask.ext import restful

from .tools import service_iden
from .api import APIException
from .service_store import service_store
from .swagger import swagger


class PassthroughServiceResource(restful.Resource):

    @swagger.operation(
        notes="""Perform a GET request using a passthrough adapter.

        <p>The parameters and response type are dependent on the particular
        service.</p>

        """
    )
    def get(self, namespace, service, path=''):
        """Perform a GET request via a passthrough adapter"""

        return self._pass_request(namespace, service, path)

    @swagger.operation(
        notes="""Perform a POST request using a passthrough adapter.

        <p>The parameters and response type are dependent on the particular
        service.</p>

        """
    )
    def post(self, namespace, service, path=''):
        """Perform a POST request via a passthrough adapter"""

        return self._pass_request(namespace, service, path)

    def _pass_request(self, namespace, service, path):
        try:
            iden = service_iden(namespace, service)
            srv = service_store[iden]['service']
        except KeyError:
            raise APIException('service not found: {}'
                               .format(service_iden(namespace, service)),
                               404)

        return srv.exec_worker(path, None, request)
