"""
Methods for turning strings and lists into EDeA dataclasses.

SPDX-License-Identifier: EUPL-1.2
"""

import pathlib
import re

from edea._type_utils import get_all_subclasses
from edea.kicad.base import KicadExpr
from edea.kicad.design_rules import DesignRules
from edea.kicad.pcb import Pcb
from edea.kicad.s_expr import QuotedStr, SExprList
from edea.kicad.schematic import Schematic

all_classes: list[KicadExpr] = get_all_subclasses(KicadExpr)


def from_list(l_expr: SExprList) -> KicadExpr:
    """
    Turn an s-expression list into an EDeA dataclass.
    """
    errors = []
    result = None
    tag_name = l_expr[0]
    # pass the rest of the list to the first class where the tag name matches
    # and it doesn't throw an error
    for cls in all_classes:
        if tag_name == cls.kicad_expr_tag_name:
            try:
                result = cls.from_list(l_expr[1:])
            except Exception as e:
                errors.append(e)
            else:
                break
    if result is None:
        if len(errors) >= 1:
            message = f"from_list [{' | -- or -- | '.join(arg for e in errors for arg in e.args)}]"
            raise ValueError(message)
        else:
            raise ValueError(f"Unknown KiCad expression starting with '{tag_name}'")
    return result


def _tokens_to_list(
    tokens: tuple[str, ...], index: int
) -> tuple[int, str | QuotedStr | SExprList]:
    if len(tokens) == index:
        raise EOFError("unexpected EOF")
    token = tokens[index]
    index += 1

    if token == "(":
        typ = tokens[index]
        index += 1

        expr: SExprList = [typ]
        while tokens[index] != ")":
            index, sub_expr = _tokens_to_list(tokens, index)
            expr.append(sub_expr)

        # remove ')'
        index += 1

        return (index, expr)

    if token == ")":
        raise SyntaxError("unexpected )")

    if token.startswith('"') and token.endswith('"'):
        token = token.removeprefix('"').removesuffix('"')
        token = token.replace("\\\\", "\\")
        token = token.replace('\\"', '"')
        token = QuotedStr(token)

    return (index, token)


_TOKENIZE_EXPR = re.compile(r'("[^"\\]*(?:\\.[^"\\]*)*"|\(|\)|"|[^\s()"]+)')


def from_str_to_list(text: str) -> SExprList:
    tokens: tuple[str, ...] = tuple(_TOKENIZE_EXPR.findall(text))
    _, expr = _tokens_to_list(tokens, 0)
    if isinstance(expr, str):
        raise ValueError(f"Expected an expression but only got a string: {expr}")
    return expr


def from_str(text: str) -> KicadExpr:
    """
    Turn a string containing KiCad s-expressions into an EDeA dataclass.
    """
    expr = from_str_to_list(text)
    return from_list(expr)


def parse_schematic(text: str) -> Schematic:
    sexpr = from_str_to_list(text)
    return Schematic.from_list(sexpr[1:])


def parse_pcb(text: str) -> Pcb:
    sexpr = from_str_to_list(text)
    return Pcb.from_list(sexpr[1:])


def parse_design_rules(text: str) -> DesignRules:
    # remove comments from the file, i.e., lines starting with `#`
    text = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("#")
    )
    # A workaround to because the file consists of seperate s-expression
    # so it gets wrapped in this expression
    sexpr = from_str_to_list(f"(design_rules {text})")
    return DesignRules.from_list(sexpr[1:])


def load_schematic(path: pathlib.Path | str) -> Schematic:
    with open(path, "r", encoding="utf-8") as f:
        return parse_schematic(f.read())


def load_pcb(path: pathlib.Path | str) -> Pcb:
    with open(path, "r", encoding="utf-8") as f:
        return parse_pcb(f.read())


def load_design_rules(path: pathlib.Path | str) -> DesignRules:
    with open(path, "r", encoding="utf-8") as f:
        return parse_design_rules(f.read())
