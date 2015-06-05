import json
import datetime
import string

from flask import request, Response
from flask.ext import restful
from prov.model import (ProvDocument, Namespace, Literal, PROV,
                        Identifier, ProvAgent)
import prov.dot

from .stores import prov_store, service_store
from .tools import service_iden
from .api import api_url_for, APIException


class ProvResource(restful.Resource):

    def get(self, namespace, service, uuid=None):
        obj = prov_store.get(uuid)
        prov_obj = to_prov(obj, namespace, service)
        fmt = request.args.get('format', 'json')
        if fmt in ('prov', 'json'):
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
         'dcterms:description': "Araport Data And Microservices API",
         'dcterms:language': "en-US",
         'dcterms:identifier': "https://api.araport.org/community/v0.3/",
         'dcterms:updated': "2015-04-17T09:44:56"})
    g.wasGeneratedBy(adama_platform, walter)
    g.wasGeneratedBy(adama_platform, vaughn)

    iden = service_iden(namespace, service)
    srv = service_store[iden]['service']
    adama_microservice = g.agent(
        ap[iden],
        {'dcterms:title': srv.name.title(),
         'dcterms:description': srv.description,
         'dcterms:language': "en-US",
         'dcterms:identifier': api_url_for('service',
                                           namespace=namespace,
                                           service=service),
         'dcterms:source': srv.git_repository
         })

    g.used(adama_microservice, adama_platform, datetime.datetime.now())

    for author in getattr(srv, 'authors', []):
        try:
            author_name = author['name']
            author_email = author['email']
        except KeyError:
            raise APIException(
                'name and email are required in author field')
        author_agent = g.agent(
            ap[slugify(author_name)],
            {'prov:type': PROV['Person'],
             'foaf:givenName': author_name,
             'foaf:mbox': '<mailto:{}>'.format(author_email)})
        sponsor_name = author.get('sponsor_organization_name', None)
        if sponsor_name:
            sponsor_agent = g.agent(
                ap[slugify(sponsor_name)],
                {'prov:type': PROV['Organization'],
                 'foaf:givenName': sponsor_name,
                 'dcterms:identifier': author.get('sponsor_uri', '')})
            g.actedOnBehalfOf(author_agent, sponsor_agent)
        g.wasGeneratedBy(adama_microservice,
                         author_agent,
                         datetime.datetime.now())

    sources_entities = process_sources(srv.sources, g, ap)
    for src in sources_entities:
        g.used(adama_microservice, src, datetime.datetime.now())

    response = g.entity(ap['adama_response'])
    g.wasGeneratedBy(response, ap[srv.type], datetime.datetime.now())
    g.used(ap[srv.type], adama_microservice, datetime.datetime.now())

    return g


def process_sources(sources, g, ap, prefix=''):
    if not sources:
        return
    for i, src in enumerate(sources):
        new_prefix = '{}{}'.format(prefix, i)
        src_entity = g.entity(
            ap['datasource_{}'.format(new_prefix)],
            {
                'dcterms:title': src.get('title', ''),
                'dcterms:description': src.get('description', ''),
                'dcterms:language': src.get('language', 'en-us'),
                'dcterms:identifier': src.get('uri', ''),
                'dcterms:updated': src.get('last_modified', ''),
                'dcterms:license': src.get('license', '')
            })
        provider = g.agent(
            ap[slugify(src['provider_name'])],
            {
                'prov:type': PROV['Person'],
                'foaf:givenName': src['provider_name'],
                'foaf:mbox': src.get('provider_email', '')
            })
        organization = g.agent(
            ap[slugify(src['sponsor_organization_name'])],
            {
                'prov:type': PROV['Organization'],
                'foaf:givenName': src['sponsor_organization_name'],
                'dcterms:identifier': src.get('sponsor_uri')
            })
        g.actedOnBehalfOf(provider, organization)
        g.wasAttributedTo(src_entity, provider)
        for nested_src in process_sources(src.get('sources', []), g, ap,
                                          prefix=new_prefix):
            g.wasDerivedFrom(src_entity, nested_src)
        yield src_entity


def slugify(text):
    """
    :type text: str
    :rtype: str
    """
    words = filter(
        lambda c: c not in string.punctuation, text.lower()).split()
    return '_'.join(words)