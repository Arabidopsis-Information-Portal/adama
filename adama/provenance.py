import json
import datetime

from flask import request, Response
from flask.ext import restful

from prov.model import (ProvDocument, Namespace, Literal, PROV,
                        Identifier, ProvAgent)
import prov.dot

from .stores import prov_store


class ProvResource(restful.Resource):

    def get(self, namespace, service, uuid):
        del namespace, service
        obj = prov_store[uuid]
        prov_obj = to_prov(obj, namespace, service)
        fmt = request.args.get('format', 'json')
        if fmt == 'json':
            return json.loads(prov_obj.serialize())
        elif fmt == 'prov-n':
            return Response(prov_obj.get_provn(),
                            content_type='text/provenance-notation')
        elif fmt == 'png':
            graph = prov.dot.prov_to_dot(prov_obj)
            graph.write_png('foo.png')
            return Response(open('foo.png'),
                            content_type='image/png')
        elif fmt == 'sources':
            return obj


def to_prov(obj, namespace, service):
    """
    :type obj: dict
    :rtype: prov.model.ProvDocument
    """
    g = ProvDocument()
    ap = Namespace('aip', 'https://araport.org/provenance/')

    g.add_namespace("dcterms", "http://purl.org/dc/terms/")
    g.add_namespace("foaf", "http://xmlns.com/foaf/0.1/")
    vaughn = g.agent(ap['matthew_vaughn'], {
        'prov:type': PROV["Person"], 'foaf:givenName': "Matthew Vaughn",
        'foaf:mbox': "<mailto:vaughn@tacc.utexas.edu>"
    })
    # Hard coded for now
    walter = g.agent(ap['walter_moreira'], {
        'prov:type': PROV["Person"], 'foaf:givenName': "Walter Moreira",
        'foaf:mbox': "<mailto:wmoreira@tacc.utexas.edu>"
    })
    utexas = g.agent(ap['university_of_texas'], {
        'prov:type': PROV["Organization"],
        'foaf:givenName': "University of Texas at Austin"
    })
    g.actedOnBehalfOf(walter, utexas)
    g.actedOnBehalfOf(vaughn, utexas)
    adama_platform = g.agent(
        ap['adama_platform'],
        {'dcterms:title': "ADAMA",
         'dcterms:description': "Araport Data and Microservices API",
         'dcterms:language':"en-US",
         'dcterms:identifier':"https://api.araport.org/community/v0.3/",
         'dcterms:updated': "2015-04-17T09:44:56"})
    g.wasGeneratedBy(adama_platform, walter)
    g.wasGeneratedBy(adama_platform, vaughn)

    microservice_name = 'mwvaughn/bar_annotation_v1.0.0'
    adama_microservice = g.agent(
        ap[microservice_name],
        {'dcterms:title': "BAR Annotation Service",
         'dcterms:description': "Returns annotation from locus ID",
         'dcterms:language': "en-US",
         'dcterms:identifier': ("https://api.araport.org/community/v0.3/"
                                "mwvaughn/bar_annotation_v1.0.0"),
         'dcterms:source': ("https://github.com/Arabidopsis-Information-"
                            "Portal/prov-enabled-api-sample")
         })

    g.wasGeneratedBy(adama_microservice, vaughn, datetime.datetime.now())
    # The microservice used the platform now
    g.used(adama_microservice, adama_platform, datetime.datetime.now())

    return g


