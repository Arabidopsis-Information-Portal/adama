from flask import request, Response
from flask.ext import restful

import prov
import prov.dot

from .stores import prov_store


class ProvResource(restful.Resource):

    def get(self, namespace, service, uuid):
        del namespace, service
        obj = prov_store[uuid]
        prov_obj = to_prov(obj)
        fmt = request.args.get('format', 'json')
        if fmt == 'json':
            return prov_obj.serialize()
        elif fmt == 'prov':
            return Response(prov_obj.get_provn(),
                            content_type='text/provenance-notation')
        elif fmt == 'png':
            graph = prov.dot.prov_to_dot(prov_obj)
            graph.write_png('foo.png')
            return Response(open('foo.png'),
                            content_type='image/png')
        elif fmt == 'sources':
            return obj


def to_prov(obj):
    """
    :type obj: dict
    :rtype: prov.model.ProvDocument
    """
    g = prov.model.ProvDocument()
    return g