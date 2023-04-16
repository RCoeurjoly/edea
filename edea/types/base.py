"""
Provides our KicadExpr class which we use as a base for all our KiCad
s-expression related dataclasses.

SPDX-License-Identifier: EUPL-1.2
"""
from collections import UserDict
from typing import Literal, Type, TypeVar, Union, get_origin

from pydantic import ValidationError
from pydantic.color import Color
from pydantic.dataclasses import dataclass

from edea.types.pcb.layers import layer_names, layer_types
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
        parsed_args, parsed_kwargs = _get_args(expr)

        if cls.kicad_expr_tag_name in ["kicad_sch", "kicad_pcb"]:
            if len(expr) <= 4:
                raise EOFError(f"Invalid {cls.kicad_expr_tag_name} file")
            if "version" in parsed_kwargs:
                cls.check_version(parsed_kwargs["version"][0][0])

        fields = Fields(cls)

        kwargs = {}
        for kw in parsed_kwargs:
            field_type = fields.type_of(kw)
            field_type_outer = fields.outer_type_of(kw)
            exp = parsed_kwargs[kw]

            if is_kicad_expr(field_type):
                # if our type says it's a list we give it the args as a list
                if field_type_outer is list:
                    kwargs[kw] = [field_type.from_list(e) for e in exp]
                else:
                    if len(exp) != 1:
                        raise ValueError(
                            f"Expecting only one item for {field_type} but got {len(exp)}: {exp[:5]}..."
                        )
                    kwargs[kw] = field_type.from_list(exp[0])
            else:
                if len(exp) != 1:
                    raise ValueError(
                        f"Expecting only one item for {field_type} but got {len(exp)}: {exp[:5]}.."
                    )
                # if it's not one of our dataclasses most often we just want to pass
                # the first and only item to `field_type` but sometimes we want to
                # make a tuple or something similar from the list of args
                # e.g. `["start", 1.0, 1.0]` -> `{"start": tuple([1.0, 1.0])}`
                if field_type_outer is tuple:
                    kwargs[kw] = tuple(exp[0])
                elif field_type_outer is list:
                    kwargs[kw] = list(exp[0])
                elif field_type is Color:
                    kwargs[kw] = Color(exp[0])

                # union types are tried till we find one that doesn't produce a
                # validation error
                # XXX this does not yet support unions that include `tuple`,
                # `list`, `Color` or `Literal`
                elif field_type_outer is Union:
                    errors = []
                    sub_fields = fields[kw].sub_fields
                    if sub_fields is None:
                        raise ValueError("Expecting sub_fields in Union")
                    for sf in sub_fields:
                        try:
                            # would be nice to not repeat logic from above here
                            sft = sf.type_
                            if is_kicad_expr(sft):
                                kwargs[kw] = sft.from_list(exp[0])
                            else:
                                kwargs[kw] = sft(exp[0][0])
                        except (ValidationError, TypeError) as e:
                            errors.append(e)
                        else:
                            break
                    if kw not in kwargs:
                        raise errors[0]

                else:
                    if len(exp[0]) != 1:
                        raise ValueError(
                            f"Expecting only one item but got {len(exp[0])}: {exp[:5]}"
                        )

                    if field_type_outer is Literal:
                        kwargs[kw] = exp[0][0]
                    else:
                        kwargs[kw] = field_type(exp[0][0])
        return cls(*parsed_args, **kwargs)

    @classmethod
    def check_version(cls, v):
        """This should be implemented by subclasses to check the file format version"""
        raise NotImplementedError


def is_kicad_expr(t):
    return isinstance(t, type) and issubclass(t, KicadExpr)


def _get_args(expr: list[list | str]) -> tuple[list[str], dict]:
    """
    Turn an s-expression list into something resembling python args and
    keyword args.
    e.g. for `["name", ["property", "foo"], ["pin", 1], ["pin", 2]]` it returns
    `(["name"], {"property": [["foo"]], "pin": [[1], [2]]})`
    """
    args = []
    index = 0
    for arg in expr:
        """
        once we hit a list we start treating it as kwargs,
        UNLESS it's a layer list.
        The `layers` field in the KiCad PCB file is as follows:
        (layers
            (0 "F.Cu" signal)
            (31 "B.Cu" signal)
            ...
        )
        So we avoid treating it as a kwarg.
        """
        if isinstance(arg, list) and not is_parsable_as_layer(arg):
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


class Fields(UserDict):
    """Add some convenience methods to the fields dict"""

    def __init__(self, cls: Type[KicadExprClass]):
        self.cls = cls
        super().__init__(cls.__pydantic_model__.__fields__)  # type: ignore

    def type_of(self, name):
        try:
            return self[name].type_
        except KeyError:
            raise KeyError(f"Found unknown field `{name}` while parsing `{self.cls}`")

    def outer_type_of(self, name):
        return get_origin(self[name].outer_type_)


def is_parsable_as_layer(value: list):
    if not isinstance(value, list) or not 3 <= len(value) <= 4:
        # A layer must be a list of 3 or 4 items.
        return False
    return value[0].isdigit() and value[1] in layer_names and value[2] in layer_types
