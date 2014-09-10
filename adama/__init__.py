#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

__author__ = 'Walter Moreira'
__email__ = 'wmoreira@tacc.utexas.edu'
__version__ = '0.1.0'

from flask import Flask, render_template, redirect, url_for
from flask_restful_swagger import swagger

app = Flask(__name__)

from .query import Query
from .register import Register, Manage
from .api import MyApi
from .config import Config
from .namespaces import NamespacesResource
from .services import ServicesResource
from .service import ServiceResource, ServiceQueryResource


api = swagger.docs(MyApi(app),
                   apiVersion='0.1',
                   basePath=Config.get('server', 'url'),
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec')

api.add_resource(NamespacesResource, '/adama')
api.add_resource(ServicesResource, '/adama/<string:namespace>/services')
api.add_resource(
    ServiceResource, '/adama/<string:namespace>/<string:service>',
    endpoint='service')
api.add_resource(
    ServiceQueryResource, '/adama/<string:namespace>/<string:service>/search',
    endpoint='search')

# api.add_resource(
#     ServiceResource, '/adama/<string:namespace>/<string:service>/search')


api.add_resource(Query, '/query')
api.add_resource(Register, '/register')
api.add_resource(Manage, '/manage/<string:adapter>/<string:command>')

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