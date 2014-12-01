#!/usr/bin/env python
import json
import pprint
import sys

from base_handler import BaseHandler


class MyHandler(BaseHandler):

    def supervisor(self):
        print 'Got a supervisor event with payload:'
        pprint.pprint(json.loads(sys.stdin.read()))
