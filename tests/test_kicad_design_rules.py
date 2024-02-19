from pathlib import Path

from edea.kicad.parser import load_design_rules


def test_loading_desing_rules():
    r = load_design_rules("tests/kicad_projects/custom_design_rules.kicad_dru")
    assert r is not None


def test_normalizing_design_rule():
    r = load_design_rules("tests/kicad_projects/custom_design_rules.kicad_dru")
    # simulate adding a rule
    r.rules = r.rules * 2
    assert len(r.rules) == 2

    # normalizing should remove the duplicate
    r.noramlize()
    assert len(r.rules) == 1


def test_extend_rules():
    r1 = load_design_rules("tests/kicad_projects/custom_design_rules.kicad_dru")
    r2 = load_design_rules("tests/kicad_projects/fixture.kicad_dru")
    r1.extend(r2)
    assert len(r1.rules) == 2


def test_rules_serialization():
    p = Path("tests/kicad_projects/custom_design_rules.kicad_dru")
    r = load_design_rules(p)
    assert str(r) == p.read_text()
