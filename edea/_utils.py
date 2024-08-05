"""
Miscellaneous utility methods that don't fit anywhere else.
"""

import re


def to_snake_case(name: str) -> str:
    """
    Converts from CamelCase to snake_case.
    From https://stackoverflow.com/a/1176023
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def remove_ref_number(ref: str) -> str:
    """
    Removes the schematic reference designator number.

    >>> remove_ref_number('R1')
    'R'

    >>> remove_ref_number('C2000')
    'C'

    >>> remove_ref_number('LED5')
    'LED'

    >>> remove_ref_number('LED')
    'LED'

    >>> remove_ref_number('lowercase2')
    'lowercase'

    >>> remove_ref_number('XYZ_whatever:2222X22222')
    'XYZ_whatever:2222X'

    """
    chars = []
    digits_stopped = False
    for c in reversed(ref):
        if not digits_stopped and c.isdigit():
            continue
        digits_stopped = True
        chars.append(c)

    return "".join(reversed(chars))
