#!/usr/bin/env python
import sys

from serf_master import SerfHandler, SerfHandlerProxy


class MinionHandler(SerfHandler):

    def start(self):
        payload = sys.stdin.read()
        print 'got payload = {}'.format(payload)


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    handler.register('minion', MinionHandler())
    handler.run()