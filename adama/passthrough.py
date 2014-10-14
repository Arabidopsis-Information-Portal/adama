from flask import Response
import requests

from .service import AbstractService


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
        method = getattr(requests, request.method.lower())
        response = method(
            self.url,
            params=request.args,
            data=request.form)
        return Response(
            response=response.content,
            status=response.status_code,
            headers=response.headers.items())

