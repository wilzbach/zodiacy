#!/usr/bin/env python3
# encoding: utf-8

import sys
import argparse
import os
import sqlite3
import json

"""import_to_sql.py: Imports the Horoscope database into a SQLite"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


parser = argparse.ArgumentParser(description="Awesome SQLite importer")
parser.add_argument('-i', '--inFile', dest='inFile', help='Input file')
parser.add_argument('-s', '--sqlFile', dest='sqlFile', help='SQLite file')
args = parser.parse_args()

if args.inFile is None:
    sys.exit("You suck")


def bufferedReader(f):
    """ Join consecutive lines of a single json line
    """
    text = None
    for line in f:
        if line[0] == "[":
            if text is not None:
                yield text
            text = line
        else:
            text += line
    yield text

#create sqlite
if os.path.exists(args.sqlFile):
    os.remove(args.sqlFile)

conn = sqlite3.connect(args.sqlFile)
c = conn.cursor()
c.execute('''CREATE TABLE horoscopes
             (sign int, keyword text, subject_line text, sms_interp text, interp text, rating real, slant text, date text)''')

with open(args.inFile) as f:
    for horoscopesStr in bufferedReader(f):
        horoscopes = json.loads(horoscopesStr)
        for h in horoscopes:
            c.execute("INSERT INTO horoscopes VALUES (?,?,?,?,?,?,?,?)",
                        (int(h['sign']), h['keyword'], h['subject_line'], h['sms_interp'], h['interp'], float(h['rating']), h['slant'], h['date']))

conn.commit()
conn.close()
