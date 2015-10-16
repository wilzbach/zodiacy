#!/usr/bin/env python3
# encoding: utf-8

import argparse
import sqlite3
import logging
from .corpus import Corpus
from os import path
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

"""generate_horoscope.py: Generates horoscopes based provided corpuses"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"

_WORDNICK_API_URL = 'http://api.wordnik.com/v4'
_WORDNICK_API_KEY = '4ee1d234e4faae42a13680b776b0e348960adc62f6f7238ed'


def restricted_weight(x, max_range=1.0):
    x = float(x)
    if x < 0.0 or x > max_range:
        raise argparse.ArgumentTypeError(
            "%r not in range [0.0, %.2f]" % (x, max_range))
    return x

here = path.abspath(path.dirname(__file__))

_parser = argparse.ArgumentParser(description="Awesome horoscope generator")
_parser.add_argument('-d', '--debug', dest='debug',
                     help='show debug logs', action='store_true')
_parser.add_argument('-a', '--database', dest='database',
                     default=path.join(here, 'data', 'zodiac.sqlite'), help='sqlite database file')
_parser.add_argument('-s', '--sign', dest='sign',
                     help='zodiac sign to generate', default=None)
_parser.add_argument('-k', '--keyword', dest='keyword',
                     help='keyword for the horoscope', default=None)
_parser.add_argument('-t', '--threshold', dest='threshold',
                     help='minimum count of horoscopes for the given filters', type=int, default=10)
_parser.add_argument('-o', '--order', dest='order',
                     help='order of the used markov chain', type=int, default=4)
_parser.add_argument('-n', '--horoscopes', dest='nr_horoscopes', choices=range(1, 10),
                     help='number of horoscopes', type=int, default=1)
_parser.add_argument('-c', '--synonyms-generation', dest='use_synonyms_generation',
                     help='additionally use synonyms of keywords for generation', action='store_true')
_parser.add_argument('-m', '--markov_type', dest='markov_type', choices=('markov', 'hmm', 'hmm_past'),
                     help='Markov type to use (default: markov)', default="markov")

_parser.add_argument('--prob-hmm-states', dest='prob_hmm_states', type=restricted_weight,
                     help='When using previous states and emissions, weight for the previous states',
                     default=0.5)
_parser.add_argument('--prob-hmm-emissions', dest='prob_hmm_emissions', type=restricted_weight,
                     help='When using previous states and emissions, weight for the previous emissions',
                     default=0.5)

_parser.add_argument('-y', '--synonyms-emission', dest='use_synonyms_emission',
                     help='use synonyms on emissions', action='store_true')
_parser.add_argument('--prob-syn-emissions', dest='prob_synonyms_emission', type=restricted_weight,
                     help='probability to emit synonyms', default=0.3)

_parser.add_argument('--list-keywords', dest='list_keywords', action='store_true',
                     help='show all available keywords')

_parser.add_argument('-r', '--random-keyword', dest='random_keyword', action='store_true',
                     help='select keyword randomly (weighted on occurrence)')


def config_logging(level):
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger('root')
    logger.setLevel(level)
    logger.addHandler(handler)


def main():
    args = _parser.parse_args()

    level = logging.DEBUG if args.debug else logging.WARNING
    config_logging(level)

    with sqlite3.connect(args.database) as conn:
        corpus = Corpus(conn, zodiac_sign=args.sign, with_rating=True,
                        with_synonyms=args.use_synonyms_generation, keyword=args.keyword,
                        wordnik_api_url=_WORDNICK_API_URL, wordnik_api_key=_WORDNICK_API_KEY)
        if args.random_keyword:
            corpus.random_keyword()

    if args.list_keywords:
        for row in corpus.list_keywords():
            print("%-4s%s" % (row[1], row[0]))
    else:
        from .markov import Markov
        mk = Markov(corpus, order=args.order,
                    use_emissions=args.markov_type[0:3] == "hmm",
                    prob_hmm_states=args.prob_hmm_states,
                    prob_hmm_emissions=args.prob_hmm_emissions,
                    use_synonyms=args.use_synonyms_emission,
                    prob_use_synonyms=args.prob_synonyms_emission)

        for _ in range(args.nr_horoscopes):
            print(mk.generate_text(args.markov_type))

if __name__ == '__main__':
    main()
