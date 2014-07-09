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
from .register import Register
from .api import MyApi
from .config import Config


api = swagger.docs(MyApi(app),
                   apiVersion='0.1',
                   basePath=Config.get('server', 'url'),
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec')

api.add_resource(Query, '/query')
api.add_resource(Register, '/register')

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