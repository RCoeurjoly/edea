import os
from hypothesis import given, infer, settings, HealthCheck

from edea.types.pcb import Pcb
from edea.types.schematic import Schematic


@settings(suppress_health_check=[HealthCheck.too_slow] if "CI" in os.environ else [])
@given(sch=infer)
def test_create_sch(sch: Schematic):
    """
    Just tests whether we can create arbitrary `Schematic` instances using
    hypothesis inference
    """
    assert sch is not None


@settings(suppress_health_check=[HealthCheck.too_slow] if "CI" in os.environ else [])
@given(pcb=infer)
def test_create_pcb(pcb: Pcb):
    """
    Just tests whether we can create arbitrary `Pcb` instances using hypothesis
    inference
    """
    assert pcb is not None
