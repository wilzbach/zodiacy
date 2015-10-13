#!/usr/bin/python

import sys
from parser import parse_horoscope

if __name__ == '__main__':
    result = parse_horoscope(sys.stdin)
    if result is not None:
        sys.stdout.write(result)
        sys.stdout.write('\n')
    else:
        sys.stderr.write('No match found.\n')
