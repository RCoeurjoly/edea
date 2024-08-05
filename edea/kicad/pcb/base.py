"""
Provides KicadPcbExpr class which we use as a base for all PCB
related KiCad s-expressions.
"""

from typing import Any, ClassVar

from edea.kicad.base import KicadExpr


class KicadPcbExpr(KicadExpr):
    """
    A KiCad PCB expression.
    """

    kicad_expr_tag_name: ClassVar[Any] = None
