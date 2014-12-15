#!/usr/bin/env python
from __future__ import print_function

import json
import os
import sys

import mischief.actors.pipe as p
import mischief.actors.actor as a
import server_actor


if __name__ == '__main__':
    ip = os.environ['IP'] or p.get_local_ip('8.8.8.8')
    print('IP = {}'.format(ip), file=sys.stderr)
    with a.Wait() as w:
        proc = a.spawn(server_actor.MinionServer, ip=ip)
        with open('/actor_info', 'w') as f:
            name, ip, port = proc.address()
            f.write(json.dumps({
                'name': name,
                'ip': ip,
                'port': port}))
        w.act()
