"""
Module for miscelaneous tools
"""

def is_str_in_concat_str(str, concat_str, sep="_"):
    """
    Function that returns True if a string is found in a concatanation of
    strings, and False otherwise.
    :param str:                 String to be found.
    :param concat_str:          Concatanation of strings
    :param sep:                 Symbol separating strings concatanated
    :return:
    """
    for str_i in concat_str.split(sep):
        if str_i == str:
            return True
    return False