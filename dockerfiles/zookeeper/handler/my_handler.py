#!/usr/bin/env python
import os
from textwrap import dedent
import sys

from serf_master import SerfHandler
from utils import truncated_stdout, serf


class MyHandler(SerfHandler):

    TEMPLATE = dedent(
        """
        tickTime=2000
        initLimit=10
        syncLimit=5
        dataDir=/data/zookeeper
        clientPort=2181
        {servers}
        """)

    @truncated_stdout
    def member_join(self):
        members = serf('members')
        myself = serf('info')['agent']['name']
        sorted_members = sort_members(members['members'])
        my = myid(myself, sorted_members)
        with open('/data/zoo.cfg', 'w') as f:
            servers = [
                'server.{i}={ip}:{port1}:{port2}'
                .format(i=i+1, ip=elt['addr'].split(':')[0],
                        port1=2888+i, port2=3888+i)
                for i, elt in enumerate(sorted_members)]
            f.write(self.TEMPLATE.format(servers='\n'.join(servers)))
        with open('/data/zookeeper/myid', 'w') as f:
            f.write(str(my))


def sort_members(members):
    assert isinstance(members, list)
    members = [elt for elt in members if elt['tags']['role'] == 'zookeeper']
    members.sort(key=lambda elt: elt['addr'])
    return members


def myid(myself, members):
    for i, elt in enumerate(members):
        if elt['name'] == myself:
            return i+1
