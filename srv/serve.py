#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys
from os import path
from bottle import route, run, response, static_file
from json import dumps
from zodiacy.wrapper import wrap_calls, wrap_corpus
from decorate import checkParams
import warnings
with warnings.catch_warnings(record=True):
    # we need to workaround the Python bug due to simplefilter('ignore')
    warnings.filterwarnings("always", category=DeprecationWarning)
    import nltk

here = path.abspath(path.dirname(__file__))
lib_path = os.path.abspath(os.path.join(here, '..'))
nltk.data.path.append(path.join(here, 'nltk_data'))
sys.path.append(lib_path)

db = path.join(here, '..', 'data', 'zodiac.sqlite')


def gen_wrapper(**attrs):
    with sqlite3.connect('file:%s?mode=ro' % db, uri=True) as conn:
        return wrap_calls(conn, **attrs)


def gen_corpus(**attrs):
    with sqlite3.connect('file:%s?mode=ro' % db, uri=True) as conn:
        return wrap_corpus(conn, **attrs)


@route("/")
def master():
    response.content_type = "text/plain"
    return static_file("README.md", root=lib_path, mimetype="text/plain")


@route("/q")
@checkParams(use_ratings=bool, use_synonyms_generation=bool,
             sign=str, keyword=str, random_keyword=bool,
             prob_hmm_states=float,
             prob_hmm_emissions=float,
             prob_synonyms_emission=float,
             markov_type=str,
             nr_horoscopes=int, format=str,
             use_synonyms=bool, order=int, order_emissions=int)
def query(**kws):
    res = gen_wrapper(**kws)
    if "format" in kws and kws["format"] == "json":
        response.content_type = 'application/json'
        return dumps(res)
    else:
        response.content_type = "text/plain"
        return "\n".join(res)


@route("/keyword/<keyword>")
def keyword(keyword):
    response.content_type = "text/plain"
    return gen_wrapper(keyword=keyword)


@route("/sign/<sign>")
def sign(sign):
    response.content_type = "text/plain"
    return gen_wrapper(sign=sign)


@route("/random-keyword")
def random_keyword():
    response.content_type = "text/plain"
    return gen_wrapper(random_keyword=True)


@route("/list-keywords")
def list_keywords():
    response.content_type = 'application/json'
    return dumps(gen_corpus().list_keywords())


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
