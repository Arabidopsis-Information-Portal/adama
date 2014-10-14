from flask import Response
import requests

from .service import AbstractService
from . import app


class PassthroughService(AbstractService):

    def __init__(self, **kwargs):
        super(PassthroughService, self).__init__(**kwargs)

    def make_image(self):
        pass

    def start_workers(self):
        pass

    def check_health(self):
        return True

    def exec_worker(self, endpoint, args, request):
        app.logger.debug('exec worker called')
        app.logger.debug('request = {}'.format(request))
        method = getattr(requests, request.method.lower())
        import ipdb; ipdb.set_trace()
        response = method(
            self.url,
            params=request.args,
            data=request.form)
        return Response(
            response=response.content,
            status=response.status_code,
            headers=response.headers.items())

