from decimal import Decimal
from typing import Type


def is_number(t: Type):
    return t is int or t is float or t is Decimal


def number_to_str(v: int | float | Decimal, *, precision=6):
    """
    Prints the number in fixed point (default: 6 decimal places) and strips
    trailing zeros and decimal point. Never uses engineering notation like
    3.134e-05.

    >>> _number_to_str(1.000)
    '1'

    >>> _number_to_str(1000)
    '1000'

    >>> _number_to_str(1.00010)
    '1.0001'

    >>> _number_to_str(2.342e-06)
    '0.000002'

    >>> _number_to_str(2.342e-06, precision=15)
    '0.000002342'

    """
    return f"{v:.{precision}f}".rstrip("0").rstrip(".")
