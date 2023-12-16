import pathlib
import subprocess
from dataclasses import dataclass


@dataclass
class Process:
    returncode: int
    stdout: str
    stderr: str


def kicad_cli(command: list[str | pathlib.Path]):
    process = subprocess.run(["kicad-cli"] + command, capture_output=True)
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
