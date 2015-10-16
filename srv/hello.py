#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from os import path
from bottle import route, run
from zodiacy.corpus import Corpus
from zodiacy.markov import Markov

here = path.abspath(path.dirname(__file__))


@route("/")
def hello_world():
        db = path.join(here, '..', 'data', 'zodiac.sqlite')
        with sqlite3.connect(db) as conn:
            corpus = Corpus(conn, keyword='pride')

        mk = Markov(corpus)
        return mk.generate_text('markov')

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
