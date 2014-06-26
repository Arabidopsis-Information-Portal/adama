"""Read config files from:

- $SRC/apim/apim.conf
- $USER/.apim.conf

"""

import ConfigParser
import os

from .tools import location_of

HERE = location_of(__file__)


def read_config():
    parser = ConfigParser.ConfigParser()
    places = [os.path.abspath(os.path.join(HERE, '../apim.conf')),
              os.path.expanduser('~/.apim.conf')]
    if not parser.read(places):
        raise RuntimeError("couldn't read config file from {0}"
                           .format(', '.join(places)))
    return parser

Config = read_config()
