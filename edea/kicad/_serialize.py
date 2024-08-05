from __future__ import annotations

import dataclasses
from types import UnionType
from typing import TYPE_CHECKING, Type, Union, get_args, get_origin

from edea._type_utils import get_full_seq_type
from edea.kicad._fields import get_type, has_meta_tag
from edea.kicad.is_kicad_expr import is_kicad_expr, is_kicad_expr_list
from edea.kicad.number import is_number, number_to_str
from edea.kicad.s_expr import QuotedStr, SExprList

if TYPE_CHECKING:
    from edea.kicad.base import KicadExpr


def to_list(kicad_expr: KicadExpr) -> SExprList:
    """This is accessed as `KicadExpr.to_list`"""
    # it's a class method in practice so accessing ._properties is ok
    # pylint: disable=protected-access
    sexpr = []
    custom_serializers = kicad_expr._edea_custom_serializers
    fields = dataclasses.fields(kicad_expr)
    for field in fields:
        value = getattr(kicad_expr, field.name)
        if custom_serializers is not None and field.name in custom_serializers:
            serializer = custom_serializers[field.name]
            sexpr += serializer(kicad_expr, value)
        else:
            sexpr += _serialize_field(field, value)
    return sexpr


def _serialize_field(field: dataclasses.Field, value) -> SExprList:
    if has_meta_tag(field, "exclude_from_files") or value is None:
        return []
    if has_meta_tag(field, "kicad_omits_default"):
        # KiCad doesn't put anything in the s-expression if this field is at
        # its default value, so we don't either.
        default = field.default
        default_factory = field.default_factory
        if default_factory is not dataclasses.MISSING:
            default = default_factory()
        if value == default:
            return []

    in_quotes = has_meta_tag(field, "kicad_always_quotes")

    if has_meta_tag(field, "kicad_no_kw"):
        field_type = get_type(field)
        # It's just the value, not an expression, i.e. a positional argument.
        return [_value_to_str(field_type, value, in_quotes)]

    if has_meta_tag(field, "kicad_kw_bool_empty"):
        # It's a keyword boolean but for some reason it's inside brackets, like
        # `(fields_autoplaced)`
        return [[field.name]] if value else []

    if has_meta_tag(field, "kicad_kw_bool"):
        # It's a keyword who's presence signifies a boolean `True`, e.g. hide is
        # `hide=True`. Here we just return the keyword so just "hide" in our
        # example.
        return [field.name] if value else []

    if has_meta_tag(field, "kicad_bool_yes_no"):
        # KiCad uses "yes" and "no" to indicate this boolean value
        return [[field.name, "yes" if value else "no"]]

    field_type = get_type(field)
    if is_kicad_expr_list(field_type):
        if value == []:
            return []
        return [[v.kicad_expr_tag_name] + v.to_list() for v in value]

    return [[field.name] + _serialize_as(field_type, value, in_quotes)]


def _serialize_as(annotation: Type, value, in_quotes) -> SExprList:
    if is_kicad_expr(annotation):
        return value.to_list()
    origin = get_origin(annotation)
    sub_types = get_args(annotation)

    if origin is tuple:
        r = []
        for i, sub in enumerate(sub_types):
            r.append(_value_to_str(sub, value[i], in_quotes))
        return r
    elif origin is list:
        sub = sub_types[0]
        if is_kicad_expr_list(annotation):
            return [_serialize_as(sub, v, in_quotes) for v in value]
        return [_value_to_str(sub, v, in_quotes) for v in value]
    if origin is Union or origin is UnionType:
        t = get_full_seq_type(value)
        return _serialize_as(t, value, in_quotes)

    return [_value_to_str(annotation, value, in_quotes)]


def _value_to_str(annotation: Type, value, in_quotes) -> str:
    make_str = QuotedStr if in_quotes else str

    if is_number(annotation):
        return make_str(number_to_str(value))

    if annotation is bool:
        return make_str("true" if value else "false")

    return make_str(value)
