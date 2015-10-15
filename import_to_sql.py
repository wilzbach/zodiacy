#!/usr/bin/env python3
# encoding: utf-8

import argparse
import os
import sqlite3
import json

"""import_to_sql.py: Imports the Horoscope database into a SQLite"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


parser = argparse.ArgumentParser(description="Awesome SQLite importer")
parser.add_argument('-i', '--inFile', dest='inFile',
                    required=True, help='Input file')
parser.add_argument('-s', '--sqlFile', dest='sqlFile',
                    required=True, help='SQLite file')
args = parser.parse_args()

# Create SQLite
if os.path.exists(args.sqlFile):
    os.remove(args.sqlFile)

with sqlite3.connect(args.sqlFile) as conn, open(args.inFile) as f:
    c = conn.cursor()
    c.execute('''CREATE TABLE horoscopes
                 (sign int, keyword text, subject_line text, sms_interp text, interp text, rating int, date text)''')

    for horoscopesStr in f:
        horoscopes = json.loads(horoscopesStr)
        if isinstance(horoscopes, dict):
            # WHY does tarot.com use different formats?
            horoscopes = horoscopes.values()
        for h in horoscopes:
            c.execute("INSERT INTO horoscopes VALUES (?,?,?,?,?,?,?)",
                      (int(h['sign']), h['keyword'], h['subject_line'],
                          h['sms_interp'], h['interp'], int(h['rating']), h['date']))
