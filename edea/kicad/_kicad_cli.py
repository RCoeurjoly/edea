import pathlib
import subprocess  # nosec
from dataclasses import dataclass
from shutil import which

from packaging.version import parse as parse_version


@dataclass
class Process:
    returncode: int
    stdout: str
    stderr: str


kicad_cli_executable = "kicad-cli"
min_kicad_cli_version = parse_version("8.0.0")


def is_kicad_cli_in_path():
    return which(kicad_cli_executable) is not None


def kicad_cli_version():
    process = subprocess.run(
        [kicad_cli_executable, "--version"], capture_output=True, check=True
    )  # nosec
    return parse_version(process.stdout.decode().strip())


is_configured = is_kicad_cli_in_path() and kicad_cli_version() >= min_kicad_cli_version


def kicad_cli(command: list[str | pathlib.Path]):
    if not is_configured:
        raise RuntimeError(
            f"KiCad CLI is not configured. Make sure {kicad_cli_executable} "
            f"is in your PATH and is at least version {min_kicad_cli_version}"
        )

    process = subprocess.run(
        [kicad_cli_executable] + command, capture_output=True, check=True
    )  # nosec
    stderr = "\n".join(
        [
            line.decode()
            for line in process.stderr.split(b"\n")
            if
            # kicad-cli lock file errors happen when we run tests in parallel but
            # don't affect anything we are doing
            line != b""
            and b"Invalid lock file" not in line
            and b"Failed to access lock" not in line
            and b"Failed to inspect the lock file" not in line
        ]
    )
    return Process(
        returncode=process.returncode,
        stdout=process.stdout.decode(),
        stderr=stderr,
    )
