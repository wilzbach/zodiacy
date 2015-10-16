import logging
import warnings
from .utils import weighted_choice
with warnings.catch_warnings(record=True):
    # we need to workaround the Python bug due to simplefilter('ignore')
    warnings.filterwarnings("always", category=DeprecationWarning)
    from nltk import pos_tag
    # loading wordnet takes about 1s
    from nltk.corpus import wordnet as wn

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


TOKENS_FOR_SYNONYMS = ["VB", "JJ", "NN", "RB"]
MAP_TOKEN_TO_WORDNET = {"VB": wn.VERB,
                        "NN": wn.NOUN, "JJ": wn.ADJ, "RB": wn.ADV}

logger = logging.getLogger('root')


def search_synonym(word):
    """ Tries to find synonyms using the WordNet API
     - Only searches synonyms for verbs (VB), adjectives (JJ), nouns (NN)
    and adverbs(RB).
    - Searches only for synonyms with the same part of speech (e.g. verb, noun)
    - Synonyms are randomly chosen with the probability weight of their path
        similarity to the given word

    Args:
        word: word to replace with a synonym
    Returns:
        synonym if we found a synonym
        word if there are no synonyms
    """
    part_of_speech = pos_tag([word])[0][1]
    if part_of_speech in TOKENS_FOR_SYNONYMS:
        assert part_of_speech in MAP_TOKEN_TO_WORDNET
        wn_pos = MAP_TOKEN_TO_WORDNET[part_of_speech]
        wn_sets = wn.synsets(word, wn_pos)
        if len(wn_sets) > 0:
            # if the synonym is part of WordNet,
            # the first entry is always our original word
            wn_start = wn_sets.pop()
            # pick a synonym different to our current word
            syns = [y for y in ((x.lemma_names()[0], wn_start.path_similarity(x))
                                for x in wn_sets) if y[0] != word]
            if len(syns) > 0:
                # we require to have existing path similarities
                min_prob_arr = list(syn for syn in syns if syn[1] is not None)
                if len(min_prob_arr) > 0:
                    w = weighted_choice(syns)
                    # WordNet API returns '_' for whitespace
                    w = w.replace("_", " ")
                    logger.debug("found synonym %s for %s", w, word)
    return word
