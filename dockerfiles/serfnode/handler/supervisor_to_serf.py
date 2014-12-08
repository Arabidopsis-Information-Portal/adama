#!/usr/bin/env python

import json
import sys

from serf import serf, serf_event


def write_stdout(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()

def main():
    while True:
        write_stdout('READY\n') # transition from ACKNOWLEDGED to READY
        line = sys.stdin.readline()  # read header line from stdin
        headers = dict(x.split(':') for x in line.split())
        data = sys.stdin.read(int(headers['len'])) # read the event payload
        data_dict = dict(x.split(':') for x in data.split())
        data_dict['eventname'] = headers['eventname']
        data_dict['node'] = serf('info')['agent']['name']
        serf_event('supervisor', json.dumps(data_dict))
        write_stdout('RESULT 2\nOK') # transition from READY to ACKNOWLEDGED

if __name__ == '__main__':
    main()
