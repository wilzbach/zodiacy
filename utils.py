__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"


def get_suffixes(arr):
    """ Returns all possible suffixes of an array (lazy evaluated)
    Args:
        arr: input array
    Returns:
        Array of all possible suffixes
    """
    arr = tuple(arr)
    return (arr[i:] for i in range(len(arr)))
