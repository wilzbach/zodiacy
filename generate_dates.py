#!/usr/bin/env python
# encoding: utf-8

from datetime import date, datetime, timedelta
from os.path import join
from os import makedirs

startDate = date(2007, 8, 1)
endDate = datetime.now()
endDate = date(endDate.year, endDate.month, endDate.day)
zodiaSigns = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces"
]

downloadFolder = "urls"
makedirs(downloadFolder, exist_ok=True)


def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta


for sign in zodiaSigns:
    with open(join(downloadFolder, sign), "w") as out:
        for res in perdelta(startDate, endDate, timedelta(days=1)):
            res = res.strftime("%Y-%m-%d")
            outHoro = "http://www.tarot.com/daily-horoscope/%s/%s" % (sign, res)
            print(outHoro, file=out)
