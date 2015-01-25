#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'Walter Moreira'
__email__ = 'wmoreira@tacc.utexas.edu'
__version__ = open('/adama-package/adama/VERSION').read().strip()

from flask import Flask

app = Flask(__name__)
app.debug = True
app.debug_log_format = ('---\n'
                        '%(asctime)s %(module)s [%(pathname)s:%(lineno)d]:\n'
                        '%(message)s')
