"""
Provides our KicadExpr class which we use as a base for all our KiCad
s-expression related dataclasses.

SPDX-License-Identifier: EUPL-1.2
"""

import dataclasses
from types import UnionType
from typing import Literal, Type, TypeVar, Union, get_args, get_origin

from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from edea.types.meta import get_meta
from edea.types.number import is_number, number_to_str
from edea.types.s_expr import QuotedStr, SExprList
from edea.util import to_snake_case

from . import _equality
from ._type_utils import get_full_seq_type

KicadExprClass = TypeVar("KicadExprClass", bound="KicadExpr")


@dataclass
class KicadExpr:
    @classmethod
    @property
    def kicad_expr_tag_name(cls: Type[KicadExprClass]):
        """
        The name that KiCad uses for this in its s-expression format. By
        default this is computed from the Python class name converted to
        snake_case but it can be overridden.
        """
        return to_snake_case(cls.__name__)

    @classmethod
    def from_list(cls: Type[KicadExprClass], expr: SExprList) -> KicadExprClass:
        """
        Turn an s-expression list of arguments into an EDeA dataclass. Note that
        you omit the tag name in the s-expression so e.g. for
        `(symbol "foo" (pin 1))` you would pass `["foo", ["pin", 1]]` to this method.
        """
        parsed_args, parsed_kwargs = _split_args(expr)

        if cls.kicad_expr_tag_name in ["kicad_sch", "kicad_pcb"]:
            if len(expr) <= 4:
                raise EOFError(f"Invalid {cls.kicad_expr_tag_name} file")
            if "version" in parsed_kwargs:
                cls.check_version(parsed_kwargs["version"][0][0])

        fields = {}
        for field in dataclasses.fields(cls):
            fields[field.name] = field

        kwargs = {}
        for kw in parsed_kwargs:
            if kw not in fields:
                raise ValueError(f"Encountered unknown field: '{kw}' for '{cls}'")
            kwargs[kw] = _parse_field(fields[kw], parsed_kwargs[kw])

        return cls(*parsed_args, **kwargs)

    def to_list(self) -> SExprList:
        sexpr = []
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            sexpr += _serialize_field(field, value)
        return sexpr

    @classmethod
    def check_version(cls, v):
        """This should be implemented by subclasses to check the file format version"""
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        for field in dataclasses.fields(self):
            v_self = getattr(self, field.name)
            v_other = getattr(other, field.name)
            if not _equality.fields_equal(field.type, v_self, v_other):
                return False
        return True


def is_kicad_expr(t) -> bool:
    return isinstance(t, type) and issubclass(t, KicadExpr)


def _serialize_field(field: dataclasses.Field, value) -> SExprList:
    if field.name == "kicad_expr_tag_name" or value is None:
        return []

    if get_meta(field, "kicad_omits_default"):
        # KiCad doesn't put anything in the s-expression if this field is at
        # its default value, so we don't either.
        default = field.default
        default_factory = field.default_factory
        if default_factory is not dataclasses.MISSING:
            default = default_factory()
        if value == default:
            return []

    in_quotes = get_meta(field, "kicad_always_quotes")

    if get_meta(field, "kicad_no_kw"):
        # It's just the value, not an expression, i.e. a positional argument.
        return [_value_to_str(field.type, value, in_quotes)]

    if get_meta(field, "kicad_kw_bool_empty"):
        # It's a keyword boolean but for some reason it's inside brackets, like
        # `(fields_autoplaced)`
        return [[field.name]] if value else []

    if get_meta(field, "kicad_kw_bool"):
        # It's a keyword who's presence signifies a boolean `True`, e.g. hide is
        # `hide=True`. Here we just return the keyword so just "hide" in our
        # example.
        return [field.name] if value else []

    if get_meta(field, "kicad_bool_yes_no"):
        # KiCad uses "yes" and "no" to indicate this boolean value
        return [[field.name, "yes" if value else "no"]]

    origin = get_origin(field.type)
    sub_types = get_args(field.type)
    if origin is list and is_kicad_expr(sub_types[0]):
        if value == []:
            return []
        return [[field.name] + v.to_list() for v in value]

    return [[field.name] + _serialize_as(field.type, value, in_quotes)]


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
        return [_value_to_str(sub, v, in_quotes) for v in value]
    if origin is Union or origin is UnionType:
        t = get_full_seq_type(value)
        return _serialize_as(t, value, in_quotes)

    return [_value_to_str(annotation, value, in_quotes)]


def _value_to_str(annotation: Type, value, in_quotes) -> str:
    make_str = QuotedStr if in_quotes else str

    if is_number(annotation):
        return make_str(number_to_str(value))

    return make_str(value)


def _parse_field(field: dataclasses.Field, exp: SExprList):
    if get_meta(field, "kicad_kw_bool_empty"):
        # It's an empty keyword boolean expression like `(fields_autoplaced)`.
        # If we are here, then it's present so we set it to `True`.
        if exp != [[]]:
            raise ValueError(f"Expecting empty expression for {field.name}, got: {exp}")
        return True
    if get_meta(field, "kicad_bool_yes_no"):
        return exp == [["yes"]]
    return _parse_as(field.type, exp)


def _parse_as(annotation: Type, exp: SExprList):
    """
    Parse an s-expression list as a particular type.
    """
    origin = get_origin(annotation)
    sub_types = get_args(annotation)

    if origin is list:
        sub = sub_types[0]
        if is_kicad_expr(sub):
            return [sub.from_list(e) for e in exp]
        _assert_len_one(annotation, exp)
        return exp[0]
    elif is_kicad_expr(annotation):
        _assert_len_one(annotation, exp)
        return annotation.from_list(exp[0])
    elif origin is tuple:
        _assert_len_one(annotation, exp)
        # XXX you can't have tuples of `KicadExpr`
        return tuple(exp[0])
    elif (origin is Union) or (origin is UnionType):
        # union types are tried till we find one that doesn't produce a
        # validation error
        errors = []
        for sub in sub_types:
            try:
                return _parse_as(sub, exp)
            except (ValidationError, TypeError) as e:
                errors.append(e)
        if len(errors) > 0:
            raise errors[0]
        else:
            raise Exception("Unknown error with parsing union type")

    _assert_len_one(annotation, exp[0])

    if origin is Literal:
        return exp[0][0]

    return annotation(exp[0][0])


def _assert_len_one(annotation, exp):
    if len(exp) != 1:
        raise ValueError(
            f"Expecting only one item for '{annotation}' but got {len(exp)}: {exp[:5]}"
        )


def _split_args(expr: SExprList) -> tuple[list[str], dict]:
    """
    Turn an s-expression list into something resembling python args and
    keyword args.
    e.g. for `["name", ["property", "foo"], ["pin", 1], ["pin", 2]]` it returns
    `(["name"], {"property": [["foo"]], "pin": [[1], [2]]})`
    """
    args = []
    index = 0
    for arg in expr:
        # Once we hit a list we start treating it as kwargs, UNLESS the keyword
        # would start with a number (which it can't in Python). This will be the
        # case for layers expressions which look like:
        #
        # (layers
        #     (0 "F.Cu" signal)
        #     (31 "B.Cu" signal)
        #     ...
        # )
        #
        if isinstance(arg, list) and not _starts_with_number(arg):
            break
        index += 1
        args.append(arg)

    if index == len(expr):
        return (args, {})

    kwarg_list = []
    for kwarg in expr[index:]:
        if isinstance(kwarg, list):
            kw = kwarg[0]
            kwarg_list.append((kw, kwarg[1:]))
        else:
            # treat positional args after keyword args as booleans
            # e.g. instance of 'hide' becomes hide=True
            kwarg_list.append((kwarg, [True]))

    # Turn a list of kwargs into a kwarg dict collecting duplicates
    # into lists.
    # e.g. `[("pin", [1]), ("pin", [2])]` becomes `{"pin": [[1], [2]]}`
    kwargs = {}
    for kw, arg in kwarg_list:
        if kw in kwargs:
            kwargs[kw].append(arg)
        else:
            kwargs[kw] = [arg]
    return (args, kwargs)


def _starts_with_number(expr: SExprList) -> bool:
    return (
        len(expr) > 0
        and isinstance(expr[0], str)
        and len(expr[0]) > 0
        and expr[0][0].isdigit()
    )
