"""
KiCad file format parser

SPDX-License-Identifier: EUPL-1.2
"""
from __future__ import annotations

import re
from _operator import methodcaller
from collections import UserList
from copy import deepcopy, copy
from dataclasses import dataclass
from typing import Dict, Tuple, Union
from uuid import UUID, uuid4

from drawable import Pts, Pad, FPLine, Polygon, Footprint, SchematicSymbol, Drawable

Symbol = str
Number = (int, float)
Atom = (Symbol, Number)

# types which have children with absolute coordinates
to_be_moved = [
    "footprint",
    "gr_text",
    "gr_poly",
    "gr_line",
    "gr_arc",
    "via",
    "segment",
    "dimension",
    "gr_circle",
    "gr_curve",
    "arc",
    "polygon",
    "filled_polygon",
]  # pts is handled separately
skip_move = ["primitives"]

# types which should be moved if their parent is in the set of "to_be_moved"
movable_types = ["at", "xy", "start", "end", "center", "mid"]

drawable_types = [
    "pin",
    "polyline",
    "rectangle",
    "wire",
    "property",
    "hierarchical_label",
    "junction",
    "text",
    "label",
    "segment",
    "via",
    "fp_text"
]
lib_symbols = {}
TOKENIZE_EXPR = re.compile(r'("[^"\\]*(?:\\.[^"\\]*)*"|\(|\)|"|[^\s()"]+)')


@dataclass
class Expr(UserList):
    """Expr lisp-y kicad expressions"""

    __slots__ = ("name", "data", "_more_than_once", "_known_attrs")

    name: str
    data: list

    _more_than_once: set
    _known_attrs: set

    def __init__(self, typ: str, *args) -> None:
        """__init__ builds a new pin with typ as the type
        passing additional arguments will append them to the list and Expr.parsed() will be called afterwards
        to update the internals.
        """
        super().__init__()
        self.name = typ
        self._known_attrs = set()
        self._more_than_once = set()

        # optionally initialize with anything thrown at init
        if len(args) > 0:
            self.extend(args)
            self.parsed()

    def __str__(self) -> str:
        sub = " ".join(map(methodcaller("__str__"), self.data))
        return f"\n({self.name} {sub})"

    def apply(self, cls, func) -> list | None:
        """
        call func on all objects in data recursively which match the type

        to call an instance method, just use e.g. v.apply(Pad, methodcaller("move_xy", x, y))
        """
        vals = []

        if isinstance(self, cls):
            ret = func(self)
            if ret is not None:
                vals.append(ret)

        if len(self.data) > 0:
            for item in self.data:
                if isinstance(item, Expr):
                    ret = item.apply(cls, func)
                    if ret is not None:
                        vals.append(ret)

        if len(vals) == 0:
            return None
        return vals

    def parsed(self):
        """subclasses can parse additional stuff out of data now"""
        # TODO: currently modifying the object and accessing fields again is not handled
        for item in self.data:
            if not isinstance(item, Expr):
                continue

            if item.name in self._known_attrs:
                if item.name not in self._more_than_once:
                    self._more_than_once.add(item.name)
            else:
                self._known_attrs.add(item.name)

    def __getattr__(self, name) -> list | dict | str:
        """
        make items from data callable via the attribute syntax
        this allows us to work with sub-expressions just like one would intuitively expect it
        combined with the index operator we can do things like: effects.font.size[0]
        this is much less verbose and conveys intent instantly.
        """
        if name not in self._known_attrs:
            return UserList.__getattribute__(self, name)

        if name not in self._more_than_once:
            for item in self.data:
                if isinstance(item, str):
                    if item == name:
                        return item
                elif item.name == name:
                    return item

        dict_items = {}
        items = []
        skip = False

        # use data[0] as dict key in case there's no duplicates
        # this allows us to access e.g. properties by their key
        for item in self.data:
            if item.name == name:
                if not skip:
                    if isinstance(item[0], Expr) or item[0] in dict_items:
                        skip = True
                    else:
                        dict_items[item[0].strip('"')] = item
                items.append(item)

        if not skip:
            return dict_items
        return items

    def __eq__(self, other) -> bool:
        """Overrides the default implementation"""
        if len(self.data) != 1:
            return self.name == other
            # raise NotImplementedError

        if other is True or other is False:
            return self[0] == "yes" and other
        if isinstance(other, Number):
            return self[0] == other.number

        return False

    def startswith(self, prefix):
        """startswith implements prefix comparison for single element lists"""
        if len(self.data) != 1:
            raise NotImplementedError

        return self[0].startswith(prefix)

    def __copy__(self):
        c = type(self)(typ=self.name)
        for name in self.__slots__:
            value = copy(getattr(self, name))
            setattr(c, name, value)
        return c

    def __deepcopy__(self, memo):
        c = type(self)(typ=self.name)
        memo[id(self)] = c
        for name in self.__slots__:
            value = deepcopy(getattr(self, name))
            setattr(c, name, value)
        return c


@dataclass(init=False)
class Movable(Expr):
    """Movable is an object with a position"""

    def move_xy(self, x: float, y: float) -> None:
        """move_xy adds the position offset x and y to the object"""
        self.data[0] += x
        self.data[1] += y


@dataclass(init=False)
class TStamp(Expr):
    """
    TStamp UUIDv4 identifiers which replace the pcbnew v5 timestamp base ones
    """

    def randomize(self):
        """randomize the tstamp UUID"""
        # parse the old uuid first to catch edgecases
        _ = UUID(self.data[0])
        # generate a new random UUIDv4
        self.data[0] = str(uuid4())


@dataclass(init=False)
class Net(Expr):
    """Schematic/PCB net"""

    def rename(self, numbers: Dict[int, int], names: Dict[str, str]):
        """rename and/or re-number a net

        A net type is either net_name with only the name (net_name "abcd"), net with only the number (net 42)
        of net with number and name (net 42 "abcd")
        """
        name_offset = 0
        if self.name == "net_name":
            net_name = self.data[0]
            net_number = None
        elif self.name == "net" and len(self.data) == 1:
            net_name = None
            net_number = self.data[0]
        else:
            name_offset = 1
            net_name = self.data[1]
            net_number = self.data[0]

        if net_name in names:
            self.data[name_offset] = names[net_name]
        if net_number in numbers:
            self.data[0] = numbers[net_number]


def from_str(program: str) -> Expr:
    """Parse KiCAD s-expr from a string"""
    tokens = TOKENIZE_EXPR.findall(program)
    _, expr = from_tokens(tokens, 0, "", "")
    return expr


def from_tokens(
        tokens: list, index: int, parent: str, grand_parent: str
) -> Tuple[int, Union[Expr, int, float, str]]:
    """Read an expression from a sequence of tokens."""
    if len(tokens) == index:
        raise SyntaxError("unexpected EOF")
    token = tokens[index]
    index += 1

    if token == "(":
        expr: Expr
        typ = tokens[index]
        index += 1

        # TODO: handle more types here
        if typ in drawable_types:
            expr = Drawable(typ)
        elif typ == "pad":
            expr = Pad(typ)
        elif typ == "footprint":
            expr = Footprint(typ)
        elif typ == "fp_line":
            expr = FPLine(typ)
        elif typ in ["polygon", "filled_polygon"]:
            expr = Polygon(typ)
        elif typ == "pts" and parent in to_be_moved and grand_parent not in skip_move:
            expr = Pts(typ)
        elif typ in movable_types and parent in to_be_moved:
            expr = Movable(typ)
        elif typ == "tstamp":
            expr = TStamp(typ)
        elif typ == "symbol":
            expr = SchematicSymbol(typ)
        else:
            expr = Expr(typ)

        while tokens[index] != ")":
            index, sub_expr = from_tokens(tokens, index, expr.name, parent)
            expr.append(sub_expr)
        index += 1  # remove ')'

        expr.parsed()

        return (index, expr)

    if token == ")":
        raise SyntaxError("unexpected )")

    # Numbers become numbers, every other token is a symbol
    try:
        return (index, int(token))
    except ValueError:
        try:
            return (index, float(token))
        except ValueError:
            return (index, Symbol(token))
