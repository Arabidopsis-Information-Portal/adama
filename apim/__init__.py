#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Walter Moreira'
__email__ = 'wmoreira@tacc.utexas.edu'
__version__ = '0.1.0'

from flask import Flask
from flask.ext import restful

from .api import Query, Register

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(Query, '/query')
api.add_resource(Register, '/register')
