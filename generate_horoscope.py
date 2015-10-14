#!/usr/bin/env python3
# encoding: utf-8

import argparse
import sqlite3
import sys
import markov

"""generate_horoscope.py: Generates horoscopes based provided corpuses"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


_parser = argparse.ArgumentParser(description="Awesome SQLite importer")
_parser.add_argument('-d', '--database', dest='database', required=True, help='sqlite database file')
_parser.add_argument('-s', '--sign', dest='sign', help='zodiac sign to generate', default=None)
_parser.add_argument('-k', '--keyword', dest='keyword', help='keyword for the horoscope', default=None)
_parser.add_argument('-t', '--threshold', dest='threshold', help='minimum count of horoscopes for the given filters', default=10)
_parser.add_argument('-o', '--order', dest='order', help='order of the used markov chain', default=4)

def keyword_valid(cursor, keyword, threshold=10):
    """ Checks whether enough horoscopes are present for the keyword """
    # TODO implement
    return True

def get_corpuses(cursor, with_rating=False, zodiac_sign=None, keyword=None):
    """ Returns a cursor with all horoscopes for the given parameters """
    # ugly code =(
    zodiac_signs = dict(zip(['general', 'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'], range(13)))
    if zodiac_sign not in zodiac_signs:
        if zodiac_sign is not None:
            raise ValueError('Invalid zodiac sign')
    else:
        zodiac_sign_ordinal = zodiac_signs[zodiac_sign]

    base_stmt = 'SELECT interp%s from horoscopes' % (',rating' if with_rating else '')
    if zodiac_sign is None:
        if keyword is None:
            return cursor.execute(base_stmt)
        else:
            return cursor.execute(base_stmt + ' WHERE keyword=?', (keyword,))
    else:
        if keyword is None:
            return cursor.execute(base_stmt + ' WHERE sign=?', (str(zodiac_sign_ordinal),))
        else:
            return cursor.execute(base_stmt + ' WHERE sign=? and keyword=?', (str(zodiac_sign_ordinal), keyword))

if __name__ == '__main__':
    args = _parser.parse_args()

    with sqlite3.connect(args.database) as conn:
        if not keyword_valid: 
            print('Not enough horoscopes for the given keyword', sys.stderr)
            sys.exit(1)
        corpuses = get_corpuses(conn.cursor(), zodiac_sign=None, keyword='enthusiasm')
        transitions = markov.compute_transitions(corpuses, args.order)
        print(len(transitions))
