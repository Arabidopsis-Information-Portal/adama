from typing import Dict, List, Union, Any, Iterator, typevar

import json
import re
import subprocess

from .exceptions import AdamaError

Ports = typevar('Ports', values=(Dict[str, List[str]],))


def decode_ports(ports: str) -> Ports:
    def split_one_map(map_str):
        internal, externals = re.split('[tu]', map_str)
        internal_port = '{}/{}'.format(
            internal, 'tcp' if 't' in map_str else 'u')
        return internal_port, externals.split(',')

    return dict(map(split_one_map,
                    [port for port in ports.split('|') if port]))


def node(role: str) -> Dict[str, Union[str, Ports]]:
    try:
        out = subprocess.check_output('serf members -format=json'.split())
        all_nodes = json.loads(out.decode('utf-8'))['members']
    except subprocess.CalledProcessError as serf_error:
        raise AdamaError("couldn't execute 'serf members'", serf_error)
    except (ValueError, KeyError) as json_error:
        raise AdamaError("error parsing output of 'serf members'", json_error)
    for a_node in select(role, all_nodes):
        tags = a_node['tags']
        return {
            'ip': tags['ip'],
            'ports': decode_ports(tags['ports']),
            'timestamp': tags['timestamp'],
            'serf_port': a_node['port'],
            'rpc_port': tags['rpc']
        }
    return {}


def select(role: str,
           nodes: List[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    for node in nodes:
        if node['status'] == 'alive' and node['tags']['role'] == role:
            yield node
