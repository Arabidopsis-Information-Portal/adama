#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

__author__ = 'Walter Moreira'
__email__ = 'wmoreira@tacc.utexas.edu'
__version__ = '0.1.0'

from flask import Flask, render_template, redirect, url_for
from flask_restful_swagger import swagger

app = Flask(__name__)

from .api import MyApi
from .config import Config
from .namespaces import NamespacesResource
from .namespace import NamespaceResource
from .services import ServicesResource
from .service import ServiceResource, ServiceQueryResource

PREFIX = Config.get('server', 'prefix')

api = swagger.docs(MyApi(app),
                   apiVersion='0.1',
                   basePath=Config.get('server', 'url'),
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec')

api.add_resource(
    NamespacesResource,
    PREFIX)
api.add_resource(
    NamespaceResource,
    '{0}/<string:namespace>'.format(PREFIX),
    endpoint='namespace')
api.add_resource(
    ServicesResource,
    '{0}/<string:namespace>/services'.format(PREFIX))
api.add_resource(
    ServiceResource,
    '{0}/<string:namespace>/<string:service>'.format(PREFIX),
    endpoint='service')
api.add_resource(
    ServiceQueryResource,
    '{0}/<string:namespace>/<string:service>/search'.format(PREFIX),
    endpoint='search')

app.debug = True
app.debug_log_format = ('---\n'
                        '%(asctime)s %(module)s [%(pathname)s:%(lineno)d]:\n'
                        '%(message)s')


@app.route('/home')
def hello_world():
    return render_template('template.html')


@app.route('/')
def root():
    return redirect(url_for('hello_world'))