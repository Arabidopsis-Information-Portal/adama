#!/usr/bin/env python
import os

from serf_master import SerfHandler, SerfHandlerProxy
try:
    from my_handler import MyHandler
except ImportError:
    MyHandler = SerfHandler


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    handler.register(os.environ.get('ROLE', 'no_role'), MyHandler())
    handler.run()