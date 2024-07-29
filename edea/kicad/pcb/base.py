"""
Provides KicadPcbExpr class which we use as a base for all PCB
related KiCad s-expressions.
"""

from edea.kicad.base import KicadExpr


class KicadPcbExpr(KicadExpr):
    """
    A KiCad PCB expression.
    """
