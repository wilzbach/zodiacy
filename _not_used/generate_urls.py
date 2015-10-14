#!/usr/bin/env python3
# encoding: utf-8

from datetime import date, datetime, timedelta
import argparse

"""generate_urls.py: Generates all possible horoscope urls"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"

parser = argparse.ArgumentParser(description="Awesome URL generator")
parser.add_argument('-o', '--outFile', dest='outFile', help='Output file')
args = parser.parse_args()


def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

startDate = date(2007, 8, 1)
endDate = datetime.now()
endDate = date(endDate.year, endDate.month, endDate.day)


with open(args.outFile, "w") as out:
    for res in perdelta(startDate, endDate, timedelta(days=1)):
        res = res.strftime("%Y-%m-%d")
        # all zodiac signs are included as JSON in every page
        outHoro = "http://www.tarot.com/daily-horoscope/aries/%s" % (res)
        print(outHoro, file=out)
