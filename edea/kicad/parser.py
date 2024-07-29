"""
Methods for turning strings and lists into EDeA dataclasses.
"""

import pathlib
import re

from edea._type_utils import get_all_subclasses
from edea.kicad.base import KicadExpr
from edea.kicad.design_rules import DesignRuleSet
from edea.kicad.pcb import Pcb
from edea.kicad.s_expr import QuotedStr, SExprList
from edea.kicad.schematic import Schematic

all_classes: list[KicadExpr] = get_all_subclasses(KicadExpr)


def from_list(l_expr: SExprList) -> KicadExpr:
    """
    Build a :py:class:`~edea.kicad.base.KicadExpr` from a list.

    :param l_expr: The KiCad S-expression list.

    :returns: The corresponding :py:class:`~edea.kicad.base.KicadExpr` instance if parsing is successful.

    :raises ValueError: If the parsing fails due to one of the following reasons:

        - No matching KiCad expression class is found for the tag name in the s-expression atom.

        - An exception occurs during the parsing attempt by a matching KiCad expression class.
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
    """
    Builds the KiCad expression structure from a sequence of KiCad expression tokens.

    :param tokens: A sequence of KiCad expression tokens.
    :param index: The starting index within the `tokens` sequence from where to begin parsing.

    :returns: A tuple containing:
      - The new index after parsing the expression (updated based on the tokens consumed).
      - The parsed KiCad expression element, which can be:
          - A plain string token.
          - A `QuotedStr` object representing a quoted string.
          - An `SExprList` object representing a nested KiCad S-expression list.

    :raises EOFError: If the end of the token sequence is reached unexpectedly while parsing a sub-expression.
    :raises SyntaxError: If an unexpected closing parenthesis `)` is encountered outside of a sub-expression.
    """
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
    """
    Parses a KiCad expression string into a corresponding S-expression recursive list.

    :param text: The KiCad expression string to be parsed.

    :returns: The parsed S-expression list representing the KiCad expression.

    :raises ValueError: If the parsing process results in a single string token instead of a complete S-expression.
    """
    tokens: tuple[str, ...] = tuple(_TOKENIZE_EXPR.findall(text))
    _, expr = _tokens_to_list(tokens, 0)
    if isinstance(expr, str):
        raise ValueError(f"Expected an expression but only got a string: {expr}")
    return expr


def from_str(text: str) -> KicadExpr:
    """
    Parses a KiCad expression string into a corresponding EDeA dataclass.

    :param text: The KiCad expression string to be parsed.

    :returns: The parsed KiCad expression object.
    """
    expr = from_str_to_list(text)
    return from_list(expr)


def parse_schematic(text: str) -> Schematic:
    """
    Parses a KiCad schematic file content into a :py:class:`~edea.kicad.schematic.__init__.Schematic`.

    :param text: The content of a KiCad schematic file.

    :returns: A Schematic object representing the parsed schematic data.
    """
    sexpr = from_str_to_list(text)
    return Schematic.from_list(sexpr[1:])


def parse_pcb(text: str) -> Pcb:
    """
    Parses a KiCad PCB file content into a :py:class:`~edea.kicad.pcb.__init__.Pcb`.

    :param text: The content of a KiCad PCB file.

    :returns: A Pcb object representing the parsed PCB data.
    """
    sexpr = from_str_to_list(text)
    return Pcb.from_list(sexpr[1:])


def parse_design_rules(text: str) -> DesignRuleSet:
    """
    Parses a KiCad design rules file content into a :py:class:`~edea.kicad.design_rules.DesignRuleSet`.

    :param text: The content of a KiCad design rules file.

    :returns: A DesignRules object representing the parsed design rules.
    """
    # remove comments from the file, i.e., lines starting with `#`
    text = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("#")
    )

    # A workaround to because the file consists of seperate s-expression
    # so it gets wrapped in this expression
    sexpr = from_str_to_list(f"(design_rules {text})")
    return DesignRuleSet.from_list(sexpr[1:])


def load_schematic(path: pathlib.Path | str) -> Schematic:
    """
    Loads a KiCad schematic file and parses its content into a :py:class:`~edea.kicad.schematic.__init__.Schematic`.

    :param path: The path to the KiCad schematic file.

    :returns: A Schematic object representing the loaded file.
    """

    with open(path, "r", encoding="utf-8") as f:
        return parse_schematic(f.read())


def load_pcb(path: pathlib.Path | str) -> Pcb:
    """
    Loads a KiCad PCB file and parses its content into a :py:class:`~edea.kicad.pcb.__init__.Pcb`.

    :param path: The path to the KiCad PCB file.

    :returns: A Pcb object representing the loaded file.
    """

    with open(path, "r", encoding="utf-8") as f:
        return parse_pcb(f.read())


def load_design_rules(path: pathlib.Path | str) -> DesignRuleSet:
    """
    Loads a KiCad design rules file and parses its content into a :py:class:`~edea.kicad.design_rules.DesignRuleSet`.

    :param path: The path to the KiCad design rules file.

    :returns: A DesignRules object representing the loaded file.
    """

    with open(path, "r", encoding="utf-8") as f:
        return parse_design_rules(f.read())
