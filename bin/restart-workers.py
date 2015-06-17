#!/usr/bin/env python

import time

import adama.command.tools as t
import adama.services as s


def main():
    for srv in s.service_store:
        print 'Restarting', srv, '...',
        t.restart_workers(srv)
        print 'ok'
        time.sleep(0.1)


if __name__ == '__main__':
   main()
