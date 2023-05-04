from hypothesis import given

import edea.types.common as common
from edea.types.base import KicadExpr
from edea.types.parser import from_list, from_str
from edea.types.serializer import to_list, from_list_to_str

from .utils import any_kicad_expr_from_module


@given(any_kicad_expr_from_module(common))
def test_serialize_common(expr: KicadExpr):
    """
    Test that serializing then parsing results in the same expression.
    """
    lst = to_list(expr)
    string = from_list_to_str(lst)
    expr2 = from_list(lst)
    assert expr2 == expr
    expr3 = from_str(string)
    assert expr3 == expr
