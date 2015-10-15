from collections import deque

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


def prefilled_buffer(start_element, length=-1):
    """ Provides an efficient circular buffer with a limited size
    Will fill the entire buffer with the start elements
    Args:
        start_element: element that will be used to fill the buffer
        length: total length of the buffer
    Returns:
        limited size buffer
    """
    assert length > 0
    return deque([start_element] * length, maxlen=length)

SENTENCE_STOPS = [".", "?", ",", ":", ";", "'"]
REPLACE_WORDS = {'n\'t': 'not', '\'ll': 'will',
                 '\'re': 'are', '\'ve': 'have', '\'s': 'is', 'ca': 'can'}


def join_tokens_to_sentences(tokens):
    """ Correctly joins tokens to multiple sentences

    Instead of always placing white-space between the tokens, it will distinguish
    between the next symbol and *not* insert whitespace if it is a sentence
    symbol (e.g. '.', or '?')

    Args:
        tokens: array of string tokens
    Returns:
        Joint sentences as one string
    """
    text = ""
    for (entry, next_entry) in zip(tokens, tokens[1:]):
        text += entry
        if next_entry not in SENTENCE_STOPS:
            text += " "

    text += tokens[-1]
    return text


def expanding_words(words):
    """ Transforms words into a their expanded form - replaces all
    abbreviations like "'ll" or "n't"

    There are some special case like can't (in tokens ("ca", "n't") where we want
    to replace both forms

    Args:
        words: words iterator to search and replace
    Returns:
        words iterator with replaced abbreviations
    """
    for word in words:
        if word in REPLACE_WORDS:
            yield REPLACE_WORDS[word]
        else:
            yield word
