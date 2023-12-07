import dataclasses
from types import UnionType
from typing import Literal, Union, get_args, get_origin

MetaTag = Literal[
    # KiCad doesn't have a keyword for the property. The property appears
    # simply as words. E.g. `top` becomes `Justify(vertical="top")` and
    # `bottom` becomes `Justify(vertical="bottom")` but KiCad never uses the
    # keyword `vertical`.
    "kicad_no_kw",
    # It's a keyword boolean like `hide` which we convert to `hide=True`.
    "kicad_kw_bool",
    # KiCad uses an empty expression, with the brackets, for this keyword boolen.
    # E.g. We parse`(fields_autoplaced)` as `fields_autoplaced=True`.
    "kicad_kw_bool_empty",
    # KiCad omits this property completely when it's all default values.
    "kicad_omits_default",
    # KiCad uses "yes" and "no" for this boolean
    "kicad_bool_yes_no",
    # KiCad always quotes this string property, no matter its contents
    "kicad_always_quotes",
]


def make_meta(*args: MetaTag):
    meta = {}
    for tag in args:
        meta[tag] = True
    return meta


def get_meta(field: dataclasses.Field, tag: MetaTag):
    return field.metadata.get(tag)


def is_optional(field: dataclasses.Field):
    if field.name == "kicad_expr_tag_name":
        return True
    if get_meta(field, "kicad_kw_bool"):
        return True
    if get_meta(field, "kicad_kw_bool_empty"):
        return True
    if get_meta(field, "kicad_omits_default"):
        return True
    origin = get_origin(field.type)
    # any list can be empty and thus omitted
    if origin is list:
        return True
    is_union = origin is Union or origin is UnionType or origin is Literal
    if not is_union:
        return False
    sub_types = get_args(field.type)
    return type(None) in sub_types or None in sub_types
