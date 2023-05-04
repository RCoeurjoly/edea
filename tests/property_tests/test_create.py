from _pytest.monkeypatch import MonkeyPatch
from hypothesis import given, infer, strategies

from edea.types.pcb import Pcb
from edea.types.schematic import Schematic

original_lists = strategies.lists


def shorter_lists(*args, **kwargs):
    """
    Generate two list items max to keep the sizes of generated examples in
    check.
    """
    kwargs["min_size"] = 0
    kwargs["max_size"] = 2
    return original_lists(*args, **kwargs)


with MonkeyPatch.context() as mp:
    mp.setattr(strategies, "lists", shorter_lists)

    @given(infer)
    def test_create_sch(expr: Schematic):
        """
        Just tests whether we can create arbitrary `Schematic` instances using
        hypothesis inference
        """
        assert expr is not None

    @given(infer)
    def test_create_pcb(expr: Pcb):
        """
        Just tests whether we can create arbitrary `Pcb` instances using hypothesis
        inference
        """
        assert expr is not None
