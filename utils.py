__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


def get_suffixes(arr):
    """ Returns all possible suffixes of an array (lazy evaluated)
    Args:
        arr: input array
    Returns:
        Array of all possible suffixes (as tuples)
    """
    arr = tuple(arr)
    return (arr[i:] for i in range(len(arr)))

SENTENCE_STOPS = [".", "?", ",", ":", ";", "'"]
JOIN_WITH_BEFORE = ['n\'t', '\'ll', '\'re', '\'ve', '\'s']


def join_tokens_to_sentences(tokens):
    """ Correctly joins tokens to multiple sentences

    Instead of always placing white-space between the tokens, it will distinguish
    between the next symbol and *not* insert whitespace if it is either a sentence
    symbol (e.g. '.', or '?') or word to join (e.g. 'll or n't)

    Args:
        tokens: array of string tokens
    Returns:
        Joint sentences as one string
    """
    text = ""
    for (entry, next_entry) in zip(tokens, tokens[1:]):
        text += entry
        if next_entry not in SENTENCE_STOPS and next_entry not in JOIN_WITH_BEFORE:
            text += " "

    text += tokens[-1]
    return text
