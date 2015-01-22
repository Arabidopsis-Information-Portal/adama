from typing import Dict, List, Tuple

import re
import subprocess

from .exceptions import AdamaError


def decode_ports(ports: str) -> Dict[str, List[str]]:
    def split_one_map(map_str):
        internal, externals = re.split('[tu]', map_str)
        internal_port = '{}/{}'.format(
            internal, 'tcp' if 't' in map_str else 'u')
        return internal_port, externals.split(',')

    return dict(map(split_one_map, ports.split('|')))


def node(role: str, port: int) -> Tuple[str, int]:
    try:
        out = subprocess.check_output('serf members -format=json'.split())
    except subprocess.CalledProcessError as exc:
        raise AdamaError("couldn't execute 'serf members'", exc, 5)
 #   json.loads(out)
