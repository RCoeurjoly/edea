from hypothesis import given, infer

from edea.kicad.pcb import Pcb
from edea.kicad.schematic import Schematic

from .config import configure_hypothesis

configure_hypothesis()


@given(infer)
def test_create_sch(_: Schematic):
    """
    Just tests whether we can create arbitrary `Schematic` instances using
    hypothesis inference.
    """


@given(infer)
def test_create_pcb(_: Pcb):
    """
    Just tests whether we can create arbitrary `Pcb` instances using hypothesis
    inference.
    """
