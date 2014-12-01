#!/usr/bin/env python
import os

from serf_master import SerfHandlerProxy
from base_handler import BaseHandler
try:
    from my_handler import MyHandler
except ImportError:
    print "Could not import user's handler."
    print "Defaulting to dummy handler."
    MyHandler = BaseHandler


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    handler.register(os.environ.get('ROLE', 'no_role'), MyHandler())
    handler.run()