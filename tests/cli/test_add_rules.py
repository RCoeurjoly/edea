import os
import re

import pytest
import pytest_mock
from typer.testing import CliRunner

from edea.cli import cli

edea_server_mock_response = {
    "name": "JLCPCB-KiCad-DRC",
    "body": """(version 1)
(rule "Pad to Silkscreen"
  (layer outer)
  (severity error)
  (condition "A.Type == 'pad' && B.Layer == '?.Silkscreen'")
  (constraint silk_clearance (min 0.1mm))
)""",
}


@pytest.fixture(autouse=True, scope="module")
def cleanup():
    """Reset the modules after tests"""
    yield
    os.system("git restore tests/kicad_projects && git clean -fd tests/kicad_projects")


def _call_cli(args: list[str]):
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join(cwd, "tests", "kicad_projects", "leako"))
        runner = CliRunner()
        return runner.invoke(
            cli,
            [
                "add",
                "rules",
                *args,
            ],
        )
    finally:
        os.chdir(cwd)


def test_add_rules_from_local_path():
    result = _call_cli(["--local-path", "../custom_design_rules.kicad_dru"])
    assert "✨ Successfully added ../custom_design_rules.kicad_dru ✨" in result.stdout
    assert result.exit_code == 0


def test_add_rules_from_git_url():
    result = _call_cli(
        [
            "--git-url",
            "https://gitlab.com/edea-dev/test-rules",
            "--path",
            "KiCad-DesignRules/JLCPCB/JLCPCB.kicad_dru",
        ]
    )
    assert (
        """⬇  Cloning https://gitlab.com/edea-dev/test-rules ...
✨ Successfully cloned https://gitlab.com/edea-dev/test-rules ✨"""
        in result.stdout
    )

    assert "KiCad-DesignRules/JLCPCB/JLCPCB.kicad_dru" in result.stdout


def test_add_rules_from_edea_url(mocker: pytest_mock.MockFixture):
    mocker.patch(
        "edea.cli.add._get_edea_module_or_rule_info",
        return_value=edea_server_mock_response,
    )
    result = _call_cli(
        [
            "--edea-url",
            "https://http://edea.com/api/v1/rules/79248d65-45a3-4ef3-a7c6-85961d335baa",
        ]
    )
    assert (
        re.search(r" Successfully added .*/(JLCPCB-KiCad-DRC.kicad_dru)", result.stdout)
        is not None
    )

    assert result.exit_code == 0
