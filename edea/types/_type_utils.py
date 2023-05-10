"""
SPDX-License-Identifier: EUPL-1.2
"""

from typing import Type


def get_full_seq_type(value: tuple | list) -> Type[tuple | list]:
    """Get the full type with type args for tuples and lists"""
    typ = type(value)
    if typ is tuple:
        sub_types: list[Type] = []
        for v in value:
            sub = type(v)
            if sub is tuple or sub is list:
                sub = get_full_seq_type(v)
            sub_types.append(sub)
        return tuple[*sub_types]  # type: ignore
    if typ is list:
        if len(value) == 0:
            return list
        v = value[0]
        sub = type(v)
        if sub is tuple or sub is list:
            sub = get_full_seq_type(v)
        return list[sub]
    return typ
