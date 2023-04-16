from hypothesis import given, infer

from edea.types.pcb import Pcb
from edea.types.schematic import Schematic


@given(sch=infer)
def test_create_sch(sch: Schematic):
    """
    Just tests whether we can create arbitrary `Schematic` instances using
    hypothesis inference
    """
    assert sch is not None


@given(pcb=infer)
def test_create_pcb(pcb: Pcb):
    """
    Just tests whether we can create arbitrary `Pcb` instances using hypothesis
    inference
    """
    assert pcb is not None
