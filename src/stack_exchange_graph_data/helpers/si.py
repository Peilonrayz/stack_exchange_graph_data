"""Simplify a number to a wanted base."""

import math
from typing import Callable, Tuple


def si_magnitude(
    base: int,
    suffix: str,
    prefixes: str,
) -> Callable[[int], Tuple[int, str]]:
    """
    SI base converter builder.

    :param base: Base to truncate values to.
    :param suffix: Suffix used to denote the type of information.
    :param prefixes: Prefixes before the suffix to denote magnitude.
    :return: A function to change a value by the above parameters.
    """
    prefixes = ' '.join(prefixes.split('|')[::-1])
    prefixes_ = prefixes.split(' ')

    def inner(value: int) -> Tuple[int, str]:
        """
        Convert a number to a truncated base form.

        :param value: Value to adjust.
        :return: Truncated value and unit.
        """
        logged = math.log(value, base)
        if -1 < value < 1:
            logged -= 1
        remainder = value / base ** int(logged)
        return remainder, prefixes_[int(logged)] + suffix
    return inner


_MAGNITUDE = 'f p n μ m| k M G T P E Z Y'


class Magnitude:
    """Magnitude conversions."""

    ibyte = si_magnitude(
        1024,
        'B',
        '| Ki Mi Gi Ti Pi Ei Zi Yi',
    )
    byte = si_magnitude(
        1000,
        'B',
        _MAGNITUDE,
    )
    number = si_magnitude(
        1000,
        '',
        _MAGNITUDE,
    )


def display(values: Tuple[int, str], decimal_places: int = 2) -> str:
    """
    Display a truncated number to a wanted DP.

    :param values: Value and unit to display.
    :param decimal_places: Amount of decimal places to display the value to.
    :return: Right aligned display value.
    """
    value, unit = values
    decimal_places = int(decimal_places)
    width = 4 + decimal_places
    if decimal_places > 0:
        return f'{value:>{width}.{decimal_places}f}{unit}'
    value = int(value)
    return f'{value:>3}{unit}'
