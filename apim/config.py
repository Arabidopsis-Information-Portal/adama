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
    parser.read([os.path.join(HERE, 'apim.conf'),
                 os.path.expanduser('~/.apim.conf')])
    return parser

Config = read_config()