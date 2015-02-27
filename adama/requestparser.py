from flask.ext import restful
from werkzeug.exceptions import ClientDisconnected

from .api import APIException


class RequestParser(restful.reqparse.RequestParser):
    """Wrap reqparse to raise APIException."""

    def parse_args(self, *args, **kwargs):
        try:
            return super(RequestParser, self).parse_args(*args, **kwargs)
        except ClientDisconnected as exc:
            raise APIException(exc.data['message'], 400)
