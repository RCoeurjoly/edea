from hypothesis import given, infer

from edea.types.pcb import Pcb
from edea.types.schematic import Schematic

from .config import configure_hypothesis

configure_hypothesis()


@given(infer)
def test_create_sch(expr: Schematic):
    """
    Just tests whether we can create arbitrary `Schematic` instances using
    hypothesis inference.
    """
    assert expr is not None


@given(infer)
def test_create_pcb(expr: Pcb):
    """
    Just tests whether we can create arbitrary `Pcb` instances using hypothesis
    inference.
    """
    assert expr is not None
