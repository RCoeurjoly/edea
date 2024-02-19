import json
from pathlib import Path

import pytest

from edea.kicad.checker import KicadDrcReporter, KicadErcReporter, check
from edea.kicad.design_rules import Severity


def test_drc():
    drc_output = KicadDrcReporter.from_kicad_file(
        "tests/kicad_projects/MP2451/MP2451.kicad_pcb"
    )
    fixture = drc_output.dict(exclude={"date"})

    with open("tests/kicad_projects/MP2451/drc.json") as f:
        output = json.load(f)

    assert fixture.keys() == output.keys()
    assert len(fixture["violations"]) == len(fixture["violations"])


def test_check_kicad_pcb_file():
    result = check("tests/kicad_projects/MP2451/MP2451.kicad_pcb")
    assert result.dr is not None
    assert len(result.dr.violations) == 10
    assert result.er is None


def test_erc():
    erc_output = KicadErcReporter.from_kicad_file(
        "tests/kicad_projects/MP2451/MP2451.kicad_sch"
    )
    fixture = erc_output.dict(exclude={"date"})

    with open("tests/kicad_projects/MP2451/erc.json") as f:
        output = json.load(f)

    assert fixture.keys() == output.keys()
    assert len(fixture["sheets"]) == len(fixture["sheets"])


def test_check_kicad_sch_file():
    result = check("tests/kicad_projects/MP2451/MP2451.kicad_sch")
    assert result.dr is None
    assert result.er is not None
    assert len(result.er.violations) == 19


def test_severity_levels():
    for level, dr_violations_num, er_violations_num in zip(
        (Severity.error, Severity.warning, Severity.ignore), (1, 10, 10), (3, 19, 19)
    ):
        result = check(
            "tests/kicad_projects/MP2451",
            level=level,
        )
        assert result.dr is not None
        assert len(result.dr.violations) == dr_violations_num
        assert result.er is not None
        assert len(result.er.violations) == er_violations_num


def test_check_kicad_pro_file():
    result = check("tests/kicad_projects/MP2451/MP2451.kicad_pro")
    assert result.dr is not None
    assert len(result.dr.violations) == 10
    assert result.er is not None
    assert len(result.er.violations) == 19


def test_check_kicad_project_dir():
    result = check("tests/kicad_projects/MP2451")
    assert result.dr is not None
    assert len(result.dr.violations) == 10
    assert result.er is not None
    assert len(result.er.violations) == 19


def test_custom_rules():
    with_custom_rules_result = check(
        "tests/kicad_projects/MP2451/MP2451.kicad_pcb",
        Path("tests/kicad_projects/custom_design_rules.kicad_dru"),
    )
    assert with_custom_rules_result.dr is not None
    assert len(with_custom_rules_result.dr.violations) == 19

    without_custom_rules_result = check("tests/kicad_projects/MP2451/MP2451.kicad_pcb")
    assert without_custom_rules_result.dr is not None
    assert len(without_custom_rules_result.dr.violations) == 10


def test_custom_rules_with_existing_rules():
    pcb_file = Path("tests/kicad_projects/ferret/ferret.kicad_pcb")
    rules_file = Path("tests/kicad_projects/ferret/ferret.kicad_dru")
    original_text = rules_file.read_text()

    with_custom_rules_result = check(
        pcb_file,
        Path("tests/kicad_projects/custom_design_rules.kicad_dru"),
    )
    assert with_custom_rules_result.dr is not None
    assert len(with_custom_rules_result.dr.violations) == 384

    without_custom_rules_result = check(pcb_file)
    assert without_custom_rules_result.dr is not None
    assert len(without_custom_rules_result.dr.violations) == 330

    assert rules_file.read_text() == original_text


def test_check_unspported_file():
    with pytest.raises(FileNotFoundError):
        check("tests/kicad_projects/custom_design_rules.kicad_dru")
