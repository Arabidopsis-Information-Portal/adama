#!/usr/bin/env python

import subprocess
import time


def main():
    subprocess.check_call('supervisorctl stop adama'.split())
    time.sleep(30)  # give time to clean
    subprocess.check_call('supervisorctl start adama'.split())
    print 'ok'


if __name__ == '__main__':
   main()
