from hypothesis import given

from edea.types.base import KicadExpr
import edea.types.common as common
from edea.types.parser import from_list, from_str
import edea.types.schematic.schematic as schematic
import edea.types.schematic.shapes as shapes
import edea.types.schematic.symbol as symbol
from edea.types.serializer import from_list_to_str, to_list

from .utils import any_kicad_expr_from_module
from .config import configure_hypothesis

configure_hypothesis()


@given(any_kicad_expr_from_module(common))
def test_serialize_common(expr: KicadExpr):
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
def test_serialize_sch_shapes(expr: KicadExpr):
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
def test_serialize_sch_symbol(expr: KicadExpr):
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
def test_serialize_schematic_expr(expr: KicadExpr):
    """
    Test that serializing then parsing `schematic` expressions results in
    the same expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr
