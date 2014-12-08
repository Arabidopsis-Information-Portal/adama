import json
import subprocess
import sys

import info


def serf(*args):
    args = list(args)
    rpc_port = info.NODE_INFO['rpc_port']
    args[1:1] = ['-rpc-addr', '127.0.0.1:{}'.format(rpc_port)]
    cmd = ['serf'] + args + ['-format=json']
    return json.loads(subprocess.check_output(cmd))


def serf_event(name, *args):
    rpc_port = info.NODE_INFO['rpc_port']
    cmd = ['serf', 'event',
           '-rpc-addr', '127.0.0.1:{}'.format(rpc_port),
           name] + list(args)
    subprocess.check_call(cmd, stdout=sys.stderr)


def where(service):
    rpc_port = info.NODE_INFO['rpc_port']
    cmd = ['serf', 'query',
           '-rpc-addr', '127.0.0.1:{}'.format(rpc_port),
           '-format=json', 'where',
           json.dumps({'role': service})]
    out = json.loads(subprocess.check_output(cmd))
    for node, response in out['Responses'].items():
        if response.endswith('SUCCESS'):
            yield json.loads(response[:-len('SUCCESS')])


def is_self(node):
    return serf('info')['agent']['name'] == node


