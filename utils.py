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
CONVERT_WORDS = {
    '\'ll': 'will',
    'n\'t': 'not',
    '\'re': 'are'
}


def join_sentence(tokens):
    """ Correctly joins tokens to multiple sentences
    Args:
        tokens: array of string tokens
    Returns:
        Joint sentences as one string
    """
    text = ""
    for entry in tokens:
        if entry not in SENTENCE_STOPS:
            text += " "
        if entry in CONVERT_WORDS:
            text += CONVERT_WORDS[entry]
        else:
            text += entry
    return text[1:]
