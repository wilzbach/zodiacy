#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from os import path
from bottle import route, run
from zodiacy.corpus import Corpus
from zodiacy.markov import Markov
import nltk
import sys

here = path.abspath(path.dirname(__file__))
lib_path = os.path.abspath(os.path.join(here, '..'))
nltk.data.path.append(path.join(here, 'nltk_data'))
sys.path.append(lib_path)


@route("/")
def hello_world():
        db = path.join(here, '..', 'data', 'zodiac.sqlite')
        with sqlite3.connect('file:%s?mode=ro' % db, uri=True) as conn:
            corpus = Corpus(conn, keyword='pride')

        mk = Markov(corpus)
        return mk.generate_text('markov')

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
