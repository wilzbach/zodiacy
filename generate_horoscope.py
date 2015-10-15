#!/usr/bin/env python3
# encoding: utf-8

import argparse
import sqlite3
import logging
from markov import Markov
from corpus import Corpus

"""generate_horoscope.py: Generates horoscopes based provided corpuses"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"

_WORDNICK_API_URL = 'http://api.wordnik.com/v4'
_WORDNICK_API_KEY = '4ee1d234e4faae42a13680b776b0e348960adc62f6f7238ed'

_parser = argparse.ArgumentParser(description="Awesome horoscope generator")
_parser.add_argument('-d', '--debug', dest='debug',
                     help='Show debug logs', action='store_true')
_parser.add_argument('-a', '--database', dest='database',
                     required=True, help='sqlite database file')
_parser.add_argument('-s', '--sign', dest='sign',
                     help='zodiac sign to generate', default=None)
_parser.add_argument('-k', '--keyword', dest='keyword',
                     help='keyword for the horoscope', default=None)
_parser.add_argument('-t', '--threshold', dest='threshold',
                     help='minimum count of horoscopes for the given filters', type=int, default=10)
_parser.add_argument('-o', '--order', dest='order',
                     help='order of the used markov chain', type=int, default=4)
_parser.add_argument('-c', '--synonym', dest='use_synonym',
                     help='Use also synonyms of keywords for generation', action='store_true')


def config_logging(level):
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger('root')
    logger.setLevel(level)
    logger.addHandler(handler)

if __name__ == '__main__':
    args = _parser.parse_args()

    level = logging.DEBUG if args.debug else logging.WARNING
    config_logging(level)

    with sqlite3.connect(args.database) as conn:
        corpus = Corpus(conn, zodiac_sign=args.sign, with_rating=True,
                        with_synonyms=args.use_synonym, keyword=args.keyword,
                        wordnik_api_url=_WORDNICK_API_URL, wordnik_api_key=_WORDNICK_API_KEY)
    mk = Markov(corpus, order=args.order, use_emissions=False)
    print(mk.generate_text())
