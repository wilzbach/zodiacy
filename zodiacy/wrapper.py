import logging
from astral import Astral
import datetime
from .corpus import Corpus

"""wrapper.py: Wraps the zodiacy horoscopes generation workflow"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"

_WORDNICK_API_URL = 'http://api.wordnik.com/v4'
_WORDNICK_API_KEY = '4ee1d234e4faae42a13680b776b0e348960adc62f6f7238ed'

logger = logging.getLogger('root')


def config_logging(level):
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)


CORPUS_ATTRS = {"use_ratings": "with_rating", "use_synonyms_generation": "with_synonyms",
                "sign": "zodiac_sign", "keyword": "keyword"}


def wrap_corpus(conn, **kws):
    level = logging.DEBUG if "debug" in kws and kws[
        "debug"] else logging.WARNING
    config_logging(level)

    attrs = {"wordnik_api_url": _WORDNICK_API_URL,
             "wordnik_api_key": _WORDNICK_API_KEY}

    for key, value in kws.items():
        if key in CORPUS_ATTRS:
            attrs[CORPUS_ATTRS[key]] = value

    corpus = Corpus(conn, **attrs)

    if "random_keyword" in kws and kws["random_keyword"]:
        corpus.random_keyword()

    if "use_moon" in kws and kws["use_moon"]:
        moon_phase = Astral().moon_phase(date=datetime.date.today())
        logger.debug("moon_phase %d", moon_phase)
        corpus.select_keyword_range(min_val=0, max_val=21, val=moon_phase)

    return corpus


MARKOV_ATTRS = {"prob_hmm_states": "prob_hmm_states",
                "prob_hmm_emissions": "prob_hmm_emissions",
                "prob_synonyms_emission": "prob_use_synonyms",
                "use_synonyms_emission": "use_synonyms",
                "order": "order", "order_emissions": "order_emissions"}


def wrap_calls(conn, **kws):
    corpus = wrap_corpus(conn, **kws)
    if "markov_type" not in kws:
        kws["markov_type"] = "markov"

    if "nr_horoscopes" not in kws:
        kws["nr_horoscopes"] = 1

    attrs = {"use_emissions": kws["markov_type"][0:3] == "hmm"}
    for key, value in kws.items():
        if key in MARKOV_ATTRS:
            attrs[MARKOV_ATTRS[key]] = value

    from .markov import Markov
    mk = Markov(corpus, **attrs)

    text = []
    for _ in range(kws["nr_horoscopes"]):
        text.append(mk.generate_text(kws["markov_type"]))
    return text
