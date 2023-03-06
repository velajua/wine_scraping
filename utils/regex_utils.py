import os
import re
import sys

from unidecode import unidecode
from typing import Union


def validator(pattern: str, extract: bool = False) -> callable:
    """
    A decorator function that takes a regular expression pattern
    and returns a function that checks if the given pattern matches
    the input string. If `extract` is True, the function returns
    the matching text, otherwise it returns True if there is a match,
    False otherwise.

    Args:
    - pattern (str): A regular expression pattern
    - extract (bool): Whether to extract the matching text
        or not (default: False)

    Returns:
    - callable: A function that checks if the given pattern
        matches the input string

    Examples:
    >>> @validator(r'^\d+$')
    ... def is_number(num: str) -> bool:
    ...     return True
    >>> is_number('123')
    True
    >>> is_number('abc')
    False
    """

    def decorator(func: callable) -> callable:
        def wrapper(text: str) -> Union[bool, str]:
            pattern_ = pattern[1:-1] if extract else pattern
            match = re.search(pattern_, text)
            return match.group() if extract and match else bool(match)
        return wrapper
    return decorator


def make_validator(pattern: str) -> callable:
    """
    A function that takes a regular expression pattern and
    returns a function that checks if the given pattern matches
    the input string. If `extract` is True, the function returns
    the matching text, otherwise it returns True if there is a match,
    False otherwise.

    Args:
    - pattern (str): A regular expression pattern

    Returns:
    - callable: A function that checks if the given pattern
        matches the input string

    Examples:
    >>> is_alpha = make_validator(r'^[a-zA-Z]+$')
    >>> is_alpha('abcd')
    True
    >>> is_alpha('123')
    False
    """

    def validator(text: str, extract: bool = False) -> Union[bool, str]:
        pattern_ = pattern[1:-1] if extract else pattern
        match = re.search(pattern_, text)
        return match.group() if extract and match else bool(match)
    return validator


def remove_symbols(x: str) -> str:
    """
    A function that removes symbols from a string
    :param x: The input string
    :type x: str
    :return: The input string with symbols removed
    :rtype: str
    """
    x = unidecode(x) if x else ''
    return re.sub(r'[^\w ]', '', x)


def remove_spaces(x: any) -> str:
    """
    A function that removes all whitespaces from a string
    :param x: The value to remove spaces from
    :type x: any
    :return: The input value with all spaces removed
    :rtype: str
    """
    return re.sub(r'\s', '', str(x))


def separate_numbers_letters(x: str) -> str:
    """
    A function that separates numbers and letters
    in a string by adding a space between them
    :param x: The input string
    :type x: str
    :return: The modified string with numbers and
        letters separated by a space
    :rtype: str
    """
    return ' '.join(re.findall(
        '[0-9]+|[a-zA-Z]+', x))


file_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
dir_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
if __name__ == "__main__" or __name__ == f"{dir_name}.{file_name}":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
