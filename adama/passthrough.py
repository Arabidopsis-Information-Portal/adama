import os
import urlparse

from flask import Response, request
from flask.ext import restful
import requests

from .service import AbstractService
from .tools import service_iden
from .api import APIException
from .service_store import service_store


class PassthroughService(AbstractService):

    def __init__(self, **kwargs):
        super(PassthroughService, self).__init__(**kwargs)

    def make_image(self):
        pass

    def start_workers(self):
        pass

    def stop_workers(self):
        pass

    def check_health(self):
        return True

    def exec_worker(self, endpoint, args, request):
        """Pass a request straight to a pre-defined url.

        ``endpoint`` is what comes after the /access endpoint, and it
        should be added to the final url.

        """
        method = getattr(requests, request.method.lower())
        data = request.data if request.data else request.form
        url = _join(self.url, endpoint)
        response = method(url, params=request.args, data=data)
        return Response(
            response=response.content,
            status=response.status_code,
            headers=response.headers.items())


def _join(url, endpoint):
    """Join endpoint at the end of url.

    Take care of considering the slashes at the end of ``url`` and at the
    beginning of ``endpoint``, each one with the proper semantics.

    """
    parsed_url = urlparse.urlsplit(url)
    new_path = os.path.join(parsed_url.path, endpoint)
    parts = list(parsed_url)
    parts[2] = new_path
    return urlparse.urlunsplit(parts)


class PassthroughServiceResource(restful.Resource):

    def get(self, namespace, service, path=''):
        try:
            iden = service_iden(namespace, service)
            srv = service_store[iden]['service']
        except KeyError:
            raise APIException('service not found: {}'
                               .format(service_iden(namespace, service)),
                               404)

        return srv.exec_worker(path, None, request)

    post = get
