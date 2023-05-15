from decimal import Decimal
from typing import Type


def is_number(t: Type):
    return t is int or t is float or t is Decimal


def number_to_str(v: int | float | Decimal, *, precision=6):
    """
    Prints the number in fixed point (default: 6 decimal places) and strips
    trailing zeros and decimal point. Never uses engineering notation like
    3.134e-05. Prints -0.0 as 0.

    >>> number_to_str(1.000)
    '1'

    >>> number_to_str(1000)
    '1000'

    >>> number_to_str(1.00010)
    '1.0001'

    >>> number_to_str(2.342e-06)
    '0.000002'

    >>> number_to_str(2.342e-06, precision=15)
    '0.000002342'

    >>> number_to_str(-0.0)
    '0'

    """
    s = f"{v:.{precision}f}".rstrip("0").rstrip(".")
    if s == "-0":
        return "0"
    return s


def numbers_equal(n1: int | float | Decimal, n2: int | float | Decimal, *, precision=6):
    p = precision
    return number_to_str(n1, precision=p) == number_to_str(n2, precision=p)
