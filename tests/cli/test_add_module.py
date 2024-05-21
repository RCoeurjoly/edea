import os

import pytest
import pytest_mock
from typer.testing import CliRunner

from edea.cli import cli

edea_server_mock_response = {
    "name": "3v3ldo",
    "repository": {
        "id": "2c6c311e-ade3-47d4-949d-939630e8cb33",
        "url": "https://gitlab.com/edea-dev/test-modules",
    },
}


@pytest.fixture(autouse=True, scope="module")
def cleanup():
    """Reset the modules after tests"""
    yield
    os.system("git restore tests/kicad_projects && git clean -fd tests/kicad_projects")


def _call_cli(args: list[str]):
    cwd = os.getcwd()
    try:
        os.chdir(os.path.join(cwd, "tests", "kicad_projects", "ferret"))
        runner = CliRunner()
        return runner.invoke(
            cli,
            [
                "add",
                "module",
                *args,
            ],
        )
    finally:
        os.chdir(cwd)


def test_add_module_from_local_dir():
    result = _call_cli(["--local-path", "../leako"])
    assert "✨ Successfully added ../leako to ferret ✨" in result.stdout
    assert result.exit_code == 0


def test_add_module_from_git_url():
    result = _call_cli(
        [
            "--git-url",
            "https://gitlab.com/edea-dev/test-modules",
            "--path",
            "3v3ldo",
        ]
    )
    assert (
        "✨ Successfully cloned https://gitlab.com/edea-dev/test-modules ✨"
        in result.stdout
    )

    assert "✨ Successfully added" in result.stdout

    assert result.exit_code == 0


def test_add_module_from_edea_url(mocker: pytest_mock.MockFixture):
    mocker.patch(
        "edea.cli.add._get_edea_module_or_rule_info",
        return_value=edea_server_mock_response,
    )
    result = _call_cli(
        [
            "--edea-url",
            "https://http://edea.com/api/v1/module/79248d65-45a3-4ef3-a7c6-85961d335baa",
        ]
    )
    assert (
        "✨ Successfully cloned https://gitlab.com/edea-dev/test-modules ✨"
        in result.stdout
    )

    assert result.exit_code == 0
