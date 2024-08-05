from types import UnionType
from typing import Type, Union, get_args, get_origin

from edea._type_utils import get_full_seq_type
from edea.kicad.number import is_number, numbers_equal


def fields_equal(annotation: Type, v1, v2):
    origin = get_origin(annotation)
    if is_number(annotation):
        return numbers_equal(v1, v2)
    elif origin is tuple:
        return _tuples_equal(annotation, v1, v2)
    elif origin is list:
        return _lists_equal(annotation, v1, v2)
    elif origin is Union or origin is UnionType:
        return _unions_equal(v1, v2)
    return v1 == v2


def _lists_equal(annotation: Type[list], lst1, lst2):
    if len(lst1) != len(lst2):
        return False
    sub_type = get_args(annotation)[0]
    return all(fields_equal(sub_type, v1, v2) for v1, v2 in zip(lst1, lst2))


def _tuples_equal(annotation: Type[tuple], t1, t2):
    sub_types = get_args(annotation)
    for i, sub in enumerate(sub_types):
        if not fields_equal(sub, t1[i], t2[i]):
            return False
    return True


def _unions_equal(v1, v2):
    t = type(v1)
    if t is not type(v2):
        return False
    if t is tuple or t is list:
        t = get_full_seq_type(v1)
    return fields_equal(t, v1, v2)
