import dataclasses
from functools import lru_cache
from types import UnionType
from typing import Annotated, Literal, Type, Union, cast, get_args, get_origin

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
    # this field is for our convenience and is not part of the kicad file format
    "exclude_from_files",
]


def make_meta(*args: MetaTag):
    # just a list for now, but we might change that later
    return args


@lru_cache(maxsize=None)
def has_meta_tag(field: dataclasses.Field, tag: MetaTag):
    origin = get_origin(field.type)
    if origin is Annotated:
        sub_types = get_args(field.type)
        metadata = sub_types[1]
        return tag in metadata
    return False


@lru_cache(maxsize=None)
def get_type(field: dataclasses.Field) -> Type:
    origin = get_origin(field.type)
    if origin is Annotated:
        sub_types = get_args(field.type)
        return sub_types[0]
    return cast(Type, field.type)


@lru_cache(maxsize=None)
def is_optional(field: dataclasses.Field):
    if has_meta_tag(field, "exclude_from_files"):
        return True
    if has_meta_tag(field, "kicad_kw_bool"):
        return True
    if has_meta_tag(field, "kicad_kw_bool_empty"):
        return True
    if has_meta_tag(field, "kicad_omits_default"):
        return True
    field_type = get_type(field)
    origin = get_origin(field_type)
    # any list can be empty and thus omitted
    if origin is list:
        return True
    is_union = origin is Union or origin is UnionType or origin is Literal
    if not is_union:
        return False
    sub_types = get_args(field_type)
    return type(None) in sub_types or None in sub_types
