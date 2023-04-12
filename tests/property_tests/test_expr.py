from hypothesis import given, infer

from edea.types.schematic import Schematic

@given(sch=infer)
def test_create_sch(sch: Schematic):
    '''Just tests wether we can create arbitrary schematics using hypothesis inference'''
    assert sch is not None
