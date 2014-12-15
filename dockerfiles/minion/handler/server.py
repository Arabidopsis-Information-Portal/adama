#!/usr/bin/env python
from __future__ import print_function

import mischief.actors.actor as a
import server_actor
from utils import serf_aware_spawn


if __name__ == '__main__':
    serf_aware_spawn(server_actor.MinionServer)
    with a.Wait() as w:
        w.act()
