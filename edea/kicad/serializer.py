"""
Methods for turning EDeA dataclasses into strings and lists.
"""

import pathlib

from edea.kicad.base import KicadExpr
from edea.kicad.pcb import Pcb
from edea.kicad.schematic import Schematic

from .s_expr import QuotedStr, SExprList


def to_list(expr: KicadExpr) -> SExprList:
    """
    Turns an EDeA dataclass (:py:class:`~edea.kicad.base.KicadExpr`) into an s-expression list.

    :param expr: The EDeA dataclass to convert.

    :returns: The s-expression list representing the dataclass.
    """
    lst: SExprList = [expr.kicad_expr_tag_name]
    return lst + expr.to_list()


_special_chars = set(
    (
        " ",
        "(",
        ")",
        '"',
        "\\",
        # instead of putting them in quotes, we should probably not allow these
        # non-printable ascii characters in our strings at all
        "\x00",
        "\x01",
        "\x02",
        "\x03",
        "\x04",
        "\x05",
        "\x06",
        "\x07",
        "\x08",
        "\x09",
        "\x0a",
        "\x0b",
        "\x0c",
        "\x0d",
        "\x0e",
        "\x0f",
        "\x10",
        "\x11",
        "\x12",
        "\x13",
        "\x14",
        "\x15",
        "\x16",
        "\x17",
        "\x18",
        "\x19",
        "\x1a",
        "\x1b",
        "\x1c",
        "\x1d",
        "\x1e",
        "\x1f",
        # non-breaking space
        "\xa0",
        # ellipses ("…"), not quite sure why we need to quote this for our
        # tokenizer but it causes parsing issues if we don't
        "\x85",
        # en quad, again not sure why we need to quote
        "\u2000",
        # em quad
        "\u2001",
        # en space
        "\u2002",
    )
)


def from_list_to_str(expr: str | QuotedStr | SExprList) -> str:
    """
    Converts an S-Expression to a string representation.

    :param expr: The expression to convert.

    :returns: The string representation of the expression.
    """

    if isinstance(expr, QuotedStr):
        return f'"{_escape(expr)}"'
    if isinstance(expr, str):
        if expr == "":
            return '""'
        elif _special_chars.intersection(expr):
            return f'"{_escape(expr)}"'
        return expr
    # a lot of newlines to make sure we never exceed kicad's maximum line
    # length
    return "(" + "\n".join([from_list_to_str(lst) for lst in expr]) + ")"


def to_str(expr: KicadExpr) -> str:
    """
    Converts a :py:class:`~edea.kicad.base.KicadExpr` to a string representation.

    :param expr: The Kicad expression to convert.

    :returns: The string representation of the Kicad expression.
    """
    return from_list_to_str(to_list(expr))


def _escape(s: str):
    """
    Escapes back-slashes and escapes double quotes.

    :param s: The string to escape.
    """
    return s.replace("\\", "\\\\").replace('"', '\\"')


def write_pcb(path: pathlib.Path | str, pcb: Pcb) -> None:
    """
    Writes a :py:class:`~edea.kicad.pcb.__init__.Pcb` to a file.

    :param path: The path to write the PCB object to.
    :param pcb: The PCB object to write.
    """
    contents = to_str(pcb)
    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)


def write_schematic(path: pathlib.Path | str, sch: Schematic) -> None:
    """
    Writes a :py:class:`~edea.kicad.schematic.__init__.Schematic` object to a file.

    :param path: The path to write the schematic object to.
    :param sch: The schematic object to write.
    """
    contents = to_str(sch)
    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)
