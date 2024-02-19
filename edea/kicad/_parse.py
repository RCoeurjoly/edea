from __future__ import annotations

import dataclasses
from reprlib import Repr
from types import UnionType
from typing import TYPE_CHECKING, Any, Literal, Type, Union, get_args, get_origin

from pydantic import ValidationError

from edea.kicad._fields import get_meta, get_type, is_optional
from edea.kicad.is_kicad_expr import is_kicad_expr, is_kicad_expr_list
from edea.kicad.s_expr import QuotedStr, SExprAtom, SExprList

ParsedKwargs = dict[str, Any]

if TYPE_CHECKING:
    from edea.kicad.base import CustomParser, KicadExpr, KicadExprClass


def from_list(cls: Type[KicadExprClass], exprs: SExprList) -> KicadExprClass:
    """This is accessed as `KicadExpr.from_list`"""
    # it's a class method in practice so accessing ._properties is ok
    # pylint: disable=protected-access
    if cls.kicad_expr_tag_name in ["kicad_sch", "kicad_pcb"]:
        if len(exprs) <= 4:
            raise EOFError(f"Invalid {cls.kicad_expr_tag_name} file")
        version = exprs[0][1]
        cls.check_version(version)

    fields = dataclasses.fields(cls)
    custom_parsers = cls._get_custom_parsers()

    try:
        parsed_kwargs, exprs = _parse(fields, exprs, custom_parsers)
    except ValidationError as e:
        raise ValueError(f"{cls._name_for_errors()} -> {e}") from e
    except (TypeError, ValueError) as e:
        args = "".join(e.args)
        raise ValueError(f"{cls._name_for_errors()} -> {args}") from e

    remaining_exprs = []

    # get rid of any remaining duplicates
    # we have seen some files with duplicate fields in the wild, even ones
    # from kicad gitlab and kicad didn't complain when opening them.
    for exp in exprs:
        # if the tag matches a field name then we assume another expression
        # for it was parsed above (or an error would have been raised) so
        # it can only be a remaining duplicate
        is_duplicate = (
            isinstance(exp, list)
            and isinstance(exp[0], SExprAtom)
            and any(field.name == exp[0] for field in fields)
        )
        if not is_duplicate:
            remaining_exprs.append(exp)

    if len(remaining_exprs) != 0:
        raise ValueError(
            f"{cls._name_for_errors()} -> Encountered unknown fields:"
            f" {remaining_exprs}"
        )

    return cls(**parsed_kwargs)


def _parse(
    fields: tuple[dataclasses.Field, ...],
    exprs: SExprList,
    custom_parsers: dict[str, CustomParser],
) -> tuple[ParsedKwargs, SExprList]:
    """
    The core parsing logic that goes through all fields and tries to get values
    for them.
    """
    # I don't know how to do this without so many branches and statements
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    parsed_kwargs = {}
    for field in fields:
        if get_meta(field, "exclude_from_files"):
            continue
        if len(exprs) == 0:
            index = fields.index(field)
            remaining = [f.name for f in fields[index:] if not is_optional(f)]
            if len(remaining) > 0:
                raise ValueError(
                    f"Didn't get enough fields. Still expecting: {remaining}"
                )
            break

        if field.name in custom_parsers:
            custom_parser = custom_parsers[field.name]
            parsed_kwargs[field.name], rest = custom_parser(exprs)
            exprs = rest
            continue

        if get_meta(field, "kicad_kw_bool"):
            if (
                isinstance(exprs[0], SExprAtom)
                # we can have text fields next to kw_bool fields so
                # technically the quotes could be the only way to tell them
                # apart
                and not isinstance(exprs[0], QuotedStr)
                and exprs[0] == field.name
            ):
                exprs.pop(0)
                parsed_kwargs[field.name] = True
            else:
                parsed_kwargs[field.name] = False
            continue

        if get_meta(field, "kicad_kw_bool_empty"):
            if (
                isinstance(exprs[0], list)
                and len(exprs[0]) > 0
                and exprs[0][0] == field.name
            ):
                exprs.pop(0)
                parsed_kwargs[field.name] = True
            else:
                parsed_kwargs[field.name] = False
            continue

        field_type = get_type(field)

        if is_kicad_expr_list(field_type):
            parsed_kwargs[field.name], rest = _collect_into_list(field_type, exprs)
            exprs = rest
            continue

        no_kw = get_meta(field, "kicad_no_kw")

        if no_kw and is_optional(field):
            if isinstance(exprs[0], SExprAtom):
                try:
                    v = _parse_atom_as(field_type, exprs[0])
                except (ValidationError, TypeError, ValueError):
                    pass
                else:
                    exprs.pop(0)
                    parsed_kwargs[field.name] = v
            continue
        if no_kw:
            exp = exprs.pop(0)
            if not isinstance(exp, SExprAtom):
                raise ValueError(f"{field.name} -> Expecting single value got: {exp}")
            parsed_kwargs[field.name] = _parse_atom_as(field_type, exp)
            continue

        found = False
        for exp in exprs:
            if isinstance(exp, list) and len(exp) > 0 and exp[0] == field.name:
                parsed_kwargs[field.name] = _parse_as(field_type, exp)
                exprs.remove(exp)
                found = True
                break
        if not found and not is_optional(field):
            raise ValueError(f"{field.name} -> Could not be found")

    return parsed_kwargs, exprs


def _collect_into_list(
    annotation: Type[list[KicadExpr]], expr: SExprList
) -> tuple[list[KicadExpr], SExprList]:
    sub_types = get_args(annotation)
    kicad_expr = sub_types[0]
    collected = (
        e[1:]
        for e in expr
        if isinstance(e, list) and e[0] == kicad_expr.kicad_expr_tag_name
    )
    rest: SExprList = [
        e
        for e in expr
        if not isinstance(e, list) or e[0] != kicad_expr.kicad_expr_tag_name
    ]
    return [kicad_expr.from_list(e) for e in collected], rest


def _parse_as(annotation: Type, expr: SExprList) -> Any:
    """
    Parse an s-expression list as a particular type.
    """

    if annotation is type(None):
        raise ValueError(
            f"(None) Expecting expression to be missing but"
            f" received something: {Repr().repr(expr)}"
        )

    kw = expr[0]
    rest = expr[1:]

    if is_kicad_expr(annotation):
        if kw != annotation.kicad_expr_tag_name:
            raise ValueError(
                f"Expecting '{annotation.kicad_expr_tag_name}', got: '{kw}'"
            )
        return annotation.from_list(rest)

    origin = get_origin(annotation)

    if origin is list:
        return _parse_as_list(annotation, rest)

    elif origin is tuple:
        # XXX you can only have tuples of simple types like str, int etc.
        return tuple(rest)
    elif (origin is Union) or (origin is UnionType):
        return _parse_as_union(annotation, expr, parse_fn=_parse_as)

    if len(rest) != 1:
        raise ValueError(
            f"Expecting only one item"
            f" of type '{annotation}' but got {len(rest)}: {rest[:5]}"
        )

    if not isinstance(rest[0], SExprAtom):
        raise ValueError(f"Expecting single value, got: {rest[0]}")

    return _parse_atom_as(annotation, rest[0])


def _parse_as_union(annotation: Type, expr: SExprList | SExprAtom, parse_fn) -> Any:
    # union types are tried till we find one that doesn't produce an error
    sub_types = get_args(annotation)
    errors = []
    for sub in sub_types:
        try:
            return parse_fn(sub, expr)
        except (ValidationError, TypeError, ValueError) as e:
            errors.append(e)
    if len(errors) > 0:
        message = (
            f"Union[{' | -- or -- | '.join(arg for e in errors for arg in e.args)}]"
        )
        raise ValueError(message)
    else:
        raise Exception("Unknown error with parsing union type")


def _parse_as_list(annotation: Type[list[Any]], rest: SExprList) -> list[Any]:
    sub_types = get_args(annotation)
    lst = []
    sub = sub_types[0]
    for e in rest:
        if not isinstance(e, SExprAtom):
            raise ValueError(
                f"Expecting only single values in list, got {type(e)}: {e}"
            )
        lst.append(_parse_atom_as(sub, e))
    return lst


def _parse_atom_as(annotation: Type, atm: SExprAtom) -> Any:
    """
    Parse single s-expression atom as a particular type.
    """
    origin = get_origin(annotation)

    if origin is list or origin is tuple:
        raise ValueError(f"Expecting multiple values, got just: '{atm}'")

    if (origin is Union) or (origin is UnionType):
        return _parse_as_union(annotation, atm, parse_fn=_parse_atom_as)

    if origin is Literal:
        sub_types = get_args(annotation)
        for sub in sub_types:
            if sub is not None:
                value = type(sub)(atm)
                if value == sub:
                    return value
        raise ValueError(f"Expecting value of type '{annotation}', got: '{atm}'.")

    if annotation is bool:
        return atm == "true" or atm == "yes"

    return annotation(atm)
