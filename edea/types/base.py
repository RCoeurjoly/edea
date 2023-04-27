"""
Provides our KicadExpr class which we use as a base for all our KiCad
s-expression related dataclasses.

SPDX-License-Identifier: EUPL-1.2
"""

from dataclasses import fields as get_dataclass_fields
from types import UnionType
from typing import Literal, Type, TypeVar, Union, get_args, get_origin

from pydantic import ValidationError
from pydantic.color import Color
from pydantic.dataclasses import dataclass

from edea.types.pcb_layers import layer_names, layer_types
from edea.util import to_snake_case

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
    def from_list(cls: Type[KicadExprClass], expr: list[list | str]) -> KicadExprClass:
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

        field_types = {}
        for f in get_dataclass_fields(cls):
            field_types[f.name] = f.type

        kwargs = {}
        for kw in parsed_kwargs:
            if kw not in field_types:
                raise ValueError(f"Encountered unknown field: '{kw}' for '{cls}'")
            kwargs[kw] = _parse_as(field_types[kw], parsed_kwargs[kw])

        return cls(*parsed_args, **kwargs)

    @classmethod
    def check_version(cls, v):
        """This should be implemented by subclasses to check the file format version"""
        raise NotImplementedError


def is_kicad_expr(t) -> bool:
    return isinstance(t, type) and issubclass(t, KicadExpr)


def _parse_as(annotation: Type, exp: list[list | str]):
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
    elif annotation is Color:
        _assert_len_one(annotation, exp)
        return Color(exp[0])  # type: ignore [return-value]
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


def _split_args(expr: list[list | str]) -> tuple[list[str], dict]:
    """
    Turn an s-expression list into something resembling python args and
    keyword args.
    e.g. for `["name", ["property", "foo"], ["pin", 1], ["pin", 2]]` it returns
    `(["name"], {"property": [["foo"]], "pin": [[1], [2]]})`
    """
    args = []
    index = 0
    for arg in expr:
        # Once we hit a list we start treating it as kwargs, UNLESS it's a
        # layer list. The `layers` field in the KiCad PCB file is as follows:
        #
        # (layers
        #     (0 "F.Cu" signal)
        #     (31 "B.Cu" signal)
        #     ...
        # )
        #
        # So we avoid treating it as a kwarg.
        if isinstance(arg, list) and not _is_parsable_as_layer(arg):
            break
        index += 1
        args.append(arg)

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
    return args, kwargs


def _is_parsable_as_layer(value: list):
    if not isinstance(value, list) or not 3 <= len(value) <= 4:
        # A layer must be a list of 3 or 4 items.
        return False
    return value[0].isdigit() and value[1] in layer_names and value[2] in layer_types
