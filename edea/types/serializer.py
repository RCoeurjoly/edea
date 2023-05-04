from edea.types.base import KicadExpr

from .s_expr import SExprList


def to_list(expr: KicadExpr) -> SExprList:
    """
    Turn an EDeA dataclass into an s-expression list.
    """
    return [expr.kicad_expr_tag_name] + expr.to_list()


_special_chars = (
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
)


def from_list_to_str(expr: str | SExprList) -> str:
    if isinstance(expr, str):
        if expr == "":
            return '""'
        elif any(c in expr for c in _special_chars):
            return f'"{_escape(expr)}"'
        return expr
    return "(" + " ".join([from_list_to_str(lst) for lst in expr]) + ")"


def _escape(s: str):
    """
    Escapes back-slashes and escapes double quotes.
    """
    return s.replace("\\", "\\\\").replace('"', '\\"')
