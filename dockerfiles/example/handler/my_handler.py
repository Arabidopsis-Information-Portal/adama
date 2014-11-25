#!/usr/bin/env python
import json
import pprint
import sys

from serf_master import SerfHandler


class MyHandler(SerfHandler):

    def supervisor(self):
        print 'Got a supervisor event with payload:'
        pprint.pprint(json.loads(sys.stdin.read()))
