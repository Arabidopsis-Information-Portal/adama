from flask.ext import restful

from .stores import prov_store


class ProvResource(restful.Resource):

    def get(self, namespace, service, uuid):
        del namespace, service
        obj = prov_store[uuid]
        return obj
