"""Read config files from:

- Deployed adama.conf inside package
- /etc/adama.conf

"""

import ConfigParser
import os
import sys

from .tools import location_of

HERE = location_of(__file__)


def read_config():
    parser = ConfigParser.ConfigParser()
    places = [os.path.abspath(os.path.join(HERE, '../adama.conf')),
              os.path.expanduser('/etc/adama.conf')]
    if not parser.read(places):
        raise RuntimeError("couldn't read config file from {0}"
                           .format(', '.join(places)))
    return parser

Config = read_config()
