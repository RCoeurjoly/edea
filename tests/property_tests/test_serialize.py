from hypothesis import given

from edea.kicad.base import KicadExpr
import edea.kicad.common as common
from edea.kicad.parser import from_list, from_str
import edea.kicad.pcb.pcb as pcb
import edea.kicad.pcb.common as pcb_common
import edea.kicad.pcb.graphics as pcb_graphics
import edea.kicad.pcb.footprint as pcb_footprint
import edea.kicad.schematic.schematic as schematic
import edea.kicad.schematic.shapes as shapes
import edea.kicad.schematic.symbol as symbol
from edea.kicad.serializer import from_list_to_str, to_list, to_str

from .config import configure_hypothesis
from .utils import any_kicad_expr_from_module

configure_hypothesis()


@given(any_kicad_expr_from_module(common))
def test_serialize_any_common(expr: KicadExpr):
    """
    Test that serializing then parsing `common` classes results in the same
    expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr


@given(any_kicad_expr_from_module(shapes))
def test_serialize_any_sch_shapes(expr: KicadExpr):
    """
    Test that serializing then parsing `schematic.shapes` results in the same
    expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr


@given(any_kicad_expr_from_module(symbol))
def test_serialize_any_sch_symbol(expr: KicadExpr):
    """
    Test that serializing then parsing `schematic.symbol` results in the same
    expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr


@given(any_kicad_expr_from_module(schematic))
def test_serialize_any_schematic_expr(expr: KicadExpr):
    """
    Test that serializing then parsing `schematic` expressions results in
    the same expression.
    """
    # we are comparing the serializer output here because an empty "path"
    # expression can be two different things
    str1 = to_str(expr)
    expr2 = from_str(str1)
    str2 = to_str(expr2)
    assert str1 == str2


@given(any_kicad_expr_from_module(pcb_common))
def test_serialize_any_pcb_common(expr: KicadExpr):
    """
    Test that serializing then parsing `pcb.common` expressions results in
    the same expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr


@given(any_kicad_expr_from_module(pcb_graphics))
def test_serialize_any_pcb_graphics(expr: KicadExpr):
    """
    Test that serializing then parsing `pcb.graphics` expressions results in
    the same expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr


@given(any_kicad_expr_from_module(pcb_footprint))
def test_serialize_any_pcb_footprint(expr: KicadExpr):
    """
    Test that serializing then parsing `pcb.footprint` expressions results in
    the same expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr


@given(any_kicad_expr_from_module(pcb))
def test_serialize_any_pcb_expr(expr: KicadExpr):
    """
    Test that serializing then parsing `pcb.pcb` expressions results in
    the same expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr
