import os
import re
import sys
import time

from functools import wraps

from typing import Callable, Union

# Decorators


def timed_retries(max_retries: int,
                  minutes: int = 1) -> Callable:
    """
    A decorator that allows a function to retry a
    specified number of times after a specified time
    interval in case of an exception

    use: @timed_retries(tries, wait_mins)

    :param max_retries: The maximum number of times to retry
    :type max_retries: int
    :param minutes: The time interval between retries in minutes
    :type minutes: int
    :return: The decorated function
    :rtype: Callable
    """
    def retry_decorator(f: Callable) -> Callable:
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            error = None
            for i in range(max_retries):
                try:
                    print(f'''retry_decorator for {
                        f.__name__} attempt:''', i)
                    return f(*args, **kwargs)
                except Exception as e:
                    time.sleep(60*minutes)
                    error = e
            print(f'''error in {f.__name__} args:{args
                  } kwargs:{kwargs} error:{error}''')
            return None
        return func_with_retries
    return retry_decorator

# Functions


def int_safe_cast(x: any) -> Union[int, None]:
    """
    A function that safely converts a value to int
    and returns None if the conversion is not possible
    :param x: The value to convert
    :type x: any
    :return: The converted int value or None
    :rtype: Union[int, None]
    """
    if x is not None:
        # Removes all non-numeric characters
        # from the input value
        x = re.sub('[^0-9.-]', '', str(x))
        # Removes the decimal part of the input value
        x = x.partition('.')[0]
        if x.isnumeric():
            return int(x)
    return None


def float_safe_cast(x: any) -> Union[float, None]:
    """
    A function that safely converts a value to float
    and returns None if the conversion is not possible
    :param x: The value to convert
    :type x: any
    :return: The converted float value or None
    :rtype: Union[float, None]
    """
    if x is not None:
        # Removes all non-numeric characters
        # from the input value
        x = re.sub('[^0-9.-]', '', str(x))
        try:
            return float(x)
        except Exception:
            return None
    return None


file_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
dir_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
if __name__ == "__main__" or __name__ == f"{dir_name}.{file_name}":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
