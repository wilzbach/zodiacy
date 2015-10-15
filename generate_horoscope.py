#!/usr/bin/env python3
# encoding: utf-8

import argparse
import sqlite3
import sys
from markov import Markov
from math import sqrt
from wordnik import swagger, WordApi

"""generate_horoscope.py: Generates horoscopes based provided corpuses"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"

_WORDNICK_API_URL = 'http://api.wordnik.com/v4'
_WORDNICK_API_KEY = '4ee1d234e4faae42a13680b776b0e348960adc62f6f7238ed'

_parser = argparse.ArgumentParser(description="Awesome horoscope generator")
_parser.add_argument('-d', '--database', dest='database', required=True, help='sqlite database file')
_parser.add_argument('-s', '--sign', dest='sign', help='zodiac sign to generate', default=None)
_parser.add_argument('-k', '--keyword', dest='keyword', help='keyword for the horoscope', default=None)
_parser.add_argument('-t', '--threshold', dest='threshold', help='minimum count of horoscopes for the given filters', type=int, default=10)
_parser.add_argument('-o', '--order', dest='order', help='order of the used markov chain', type=int, default=4)
_parser.add_argument('-c', '--synonym', dest='use_synonym', help='Use also synonyms of keywords for generation', action='store_true')

def keyword_valid(cursor, keyword, threshold=10):
    """ Checks whether enough horoscopes are present for the keyword """
    count = cursor.execute('SELECT COUNT(*) AS count WHERE keyword=?', (keyword,))
    if len(count) > 0 and count[0] > threshold:
        return True

def get_synonyms(keyword):
    client = swagger.ApiClient(_WORDNICK_API_KEY, _WORDNICK_API_URL)
    word_api = WordApi.WordApi(client)
    return word_api.getRelatedWords(keyword, relationshipTypes='synonym')[0].words

def get_present_synonyms(cursor, keyword):
    synonyms = get_synonyms(keyword)
    cursor.execute('SELECT keyword FROM horoscopes WHERE keyword IN (%s) GROUP BY keyword' % ','.join('?' for _ in synonyms), tuple(synonyms))
    return [row[0] for row in cursor if row is not None]

def get_corpus(conn, with_rating=False, with_synonyms=False, zodiac_sign=None, keyword=None):
    """ Returns a cursor with all horoscopes for the given parameters """
    # ugly code =(
    zodiac_signs = dict(zip(['general', 'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'], range(13)))
    synonym_influence = 0.2
    if zodiac_sign not in zodiac_signs:
        if zodiac_sign is not None:
            raise ValueError('Invalid zodiac sign')
    else:
        zodiac_sign_ordinal = zodiac_signs[zodiac_sign]

    base_stmt = 'SELECT interp%s,keyword from horoscopes' % (',rating' if with_rating else '')
    cursor = conn.cursor()
    if zodiac_sign is None:
        if keyword is None:
            cursor.execute(base_stmt)
            return ((row[0], row[1]) for row in cursor) if with_rating else ((row[0],) for row in cursor)
        else:
            synonyms = get_present_synonyms(conn.cursor(), args.keyword)
            cursor.execute(base_stmt + ' WHERE keyword=?', (keyword,))
            cursor.execute(base_stmt + ' WHERE keyword in (%s)' % ','.join(('?' for _ in synonyms)), (*synonyms,))
            return ((row[0], row[1] if row[2] is keyword else synonym_influence*row[1]*sqrt(len(synonyms))) for row in cursor) if with_rating else ((row[0],) for row in cursor if row is not None)
    else:
        if keyword is None:
            cursor.execute(base_stmt + ' WHERE sign=?', (str(zodiac_sign_ordinal),))
            return ((row[0], row[1]) for row in cursor) if with_rating else ((row[0],) for row in cursor if row is not None)
        else:
            synonyms = get_present_synonyms(conn.cursor(), args.keyword)
            cursor.execute(base_stmt + ' WHERE sign=? and keyword=?', (str(zodiac_sign_ordinal), keyword))
            cursor.execute(base_stmt + ' WHERE sign=? and keyword in (%s)' % ','.join(('?' for _ in synonyms)), (str(zodiac_sign_ordinal), *synonyms))
            return ((row[0], row[1] if row[2] is keyword else synonym_influence*row[1]*sqrt(len(synonyms))) for row in cursor) if with_rating else ((row[0],) for row in cursor if row is not None)

if __name__ == '__main__':
    args = _parser.parse_args()

    with sqlite3.connect(args.database) as conn:
        if not keyword_valid:
            print('Not enough horoscopes for the given keyword', sys.stderr)
            sys.exit(1)
        corpus = get_corpus(conn, zodiac_sign=None, with_rating=True, with_synonyms=args.use_synonym, keyword=args.keyword)
        mk = Markov(corpus, order=args.order)
        print(mk.generate_text(5))
        print(mk.generate_text(5))
        print(mk.generate_text(5))
        print(mk.generate_text(5))
