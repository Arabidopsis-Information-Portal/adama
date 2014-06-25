#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

__author__ = 'Walter Moreira'
__email__ = 'wmoreira@tacc.utexas.edu'
__version__ = '0.1.0'

from flask import Flask
from flask_restful_swagger import swagger

from .query import Query
from .register import Register
from .api import MyApi


app = Flask(__name__)
api = swagger.docs(MyApi(app),
                   apiVersion='0.1',
                   basePath='http://localhost:8000',
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec')

api.add_resource(Query, '/query')
api.add_resource(Register, '/register')
