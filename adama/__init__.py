#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os

from .tools import location_of
from .ip_pool import IPPoolServer

HERE = location_of(__file__)

__author__ = 'Walter Moreira'
__email__ = 'wmoreira@tacc.utexas.edu'
__version__ = open(os.path.join(HERE, 'VERSION')).read().strip()

from flask import Flask

app = Flask(__name__)
app.debug = True
app.debug_log_format = ('---\n'
                        '%(asctime)s %(module)s [%(pathname)s:%(lineno)d]:\n'
                        '%(message)s')

IPPoolServer()