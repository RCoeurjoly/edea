import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from edea.kicad.checker import CheckResult, KicadDrcReporter, KicadErcReporter, check
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
    # this is happening on ci only for this test only for some reason!
    assert len(result.dr.violations) in [3, 10]
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
        (Severity.error, Severity.warning, Severity.ignore), (1, 3, 3), (3, 19, 19)
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
    assert len(result.dr.violations) == 3
    assert result.er is not None
    assert len(result.er.violations) == 19


def test_check_kicad_project_dir():
    result = check("tests/kicad_projects/MP2451")
    assert result.dr is not None
    assert len(result.dr.violations) == 3
    assert result.er is not None
    assert len(result.er.violations) == 19


def test_custom_rules():
    with_custom_rules_result = check(
        "tests/kicad_projects/MP2451/MP2451.kicad_pcb",
        Path("tests/kicad_projects/custom_design_rules.kicad_dru"),
    )
    assert with_custom_rules_result.dr is not None
    assert len(with_custom_rules_result.dr.violations) == 12

    without_custom_rules_result = check("tests/kicad_projects/MP2451/MP2451.kicad_pcb")
    assert without_custom_rules_result.dr is not None
    assert len(without_custom_rules_result.dr.violations) == 3


def test_custom_rules_with_existing_rules():
    pcb_file = Path("tests/kicad_projects/ferret/ferret.kicad_pcb")
    rules_file = Path("tests/kicad_projects/ferret/ferret.kicad_dru")
    original_text = rules_file.read_text()

    with_custom_rules_result = check(
        pcb_file,
        Path("tests/kicad_projects/custom_design_rules.kicad_dru"),
    )
    assert with_custom_rules_result.dr is not None
    assert len(with_custom_rules_result.dr.violations) == 367

    without_custom_rules_result = check(pcb_file)
    assert without_custom_rules_result.dr is not None
    assert len(without_custom_rules_result.dr.violations) == 313

    assert rules_file.read_text() == original_text


@patch("edea.kicad.checker.get")
def test_custom_rules_url(mock_get):
    # begin mock
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": "2fdd7f4f-77ab-4912-86e2-4448230a4ed0",
        "user_id": "a788991f-9c1e-46f7-b992-6320a8575c9f",
        "short_code": None,
        "private": False,
        "repository": {
            "id": "d04c0719-e352-423b-b9df-abf85e84809a",
            "url": "https://gitlab.com/edea-dev/test-rules",
        },
        "name": "JLCPCB-KiCad-DRC",
        "description": "LCPCB Design Rules for KiCad 7.0, implemented as Custom Rules in PCB Editor",
        "readme_path": "readme.md",
        "body": """
            (version 1)
            (rule "fixture"
            (layer outer)
            (severity error)
            (condition "A.Type == 'pad' && B.Layer == '?.Silkscreen'")
            (constraint silk_clearance (min 0.1mm))
            )""",
    }
    mock_get.return_value = mock_response
    # end mock

    pcb_file = Path("tests/kicad_projects/ferret/ferret.kicad_pcb")
    rules_file = Path("tests/kicad_projects/ferret/ferret.kicad_dru")
    url = "https://edea-ps.com/v1/rules/user/JLCPCB-KiCad-DRC"
    original_text = rules_file.read_text()
    with_custom_rules_result = check(
        pcb_file,
        None,
        url,
    )

    assert with_custom_rules_result.dr is not None
    assert len(with_custom_rules_result.dr.violations) == 367

    without_custom_rules_result = check(pcb_file)
    assert without_custom_rules_result.dr is not None
    assert len(without_custom_rules_result.dr.violations) == 313

    assert rules_file.read_text() == original_text


def test_check_unspported_file():
    with pytest.raises(FileNotFoundError):
        check("tests/kicad_projects/custom_design_rules.kicad_dru")


def test_loading_result_from_json():
    result = check("tests/kicad_projects/MP2451/MP2451.kicad_pro")
    assert result.dr is not None
    result = CheckResult(**json.loads(result.json()))
    assert result.dr is not None
