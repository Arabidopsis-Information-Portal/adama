#!/usr/bin/env python

import mischief.actors.actor as a
import server_actor


if __name__ == '__main__':
    with a.Wait() as w:
        a.spawn(server_actor.MinionServer)
        w.act()
