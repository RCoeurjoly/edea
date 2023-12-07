"""
Methods for turning strings and lists into EDeA dataclasses.

SPDX-License-Identifier: EUPL-1.2
"""
import re

# we need to import these unused modules for get_all_subclasses to work
import edea.kicad.pcb  # noqa F401
import edea.kicad.schematic  # noqa: F401
from edea._type_utils import get_all_subclasses
from edea.kicad.base import KicadExpr
from edea.kicad.s_expr import QuotedStr, SExprList

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
            raise errors[0]
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
