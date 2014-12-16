#!/usr/bin/env python

import os
import sys

import actors
from utils import serf_aware_spawn


def start(actor_name):
    obj = getattr(actors, actor_name)
    with serf_aware_spawn(obj, actor_name) as p:
        os.waitpid(p.pid, 0)


if __name__ == '__main__':
    actor_name = sys.argv[1]
    start(actor_name)
