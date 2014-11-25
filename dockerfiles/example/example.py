#!/usr/bin/env python
import itertools
import time

def main():
    for i in itertools.count():
        print i
        time.sleep(1)

if __name__ == '__main__':
    main()