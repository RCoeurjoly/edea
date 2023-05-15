"""
Test that parses then serializes as many KiCad 6 projects as we could find.

SPDX-License-Identifier: EUPL-1.2
"""

import os
import subprocess

import pytest

from edea.types.common import VersionError
from edea.types.parser import from_str
from edea.types.schematic import Schematic
from edea.types.serializer import to_str

test_folder = os.path.dirname(os.path.realpath(__file__))
kicad_folder = os.path.join(test_folder, "kicad_projects/kicad6-test-files")

kicad_sch_files = []
kicad_pcb_files = []
for root, dirs, files in os.walk(kicad_folder):
    for file in files:
        path = os.path.join(root, file)
        if file.endswith(".kicad_sch"):
            kicad_sch_files.append(path)
        elif file.endswith(".kicad_pcb"):
            kicad_pcb_files.append(path)


@pytest.mark.parametrize("sch_path", kicad_sch_files)
def test_serialize_all_sch_files(sch_path, tmp_path_factory):
    with open(sch_path, encoding="utf-8") as f:
        try:
            sch = from_str(f.read())
        except (VersionError, EOFError) as e:
            return pytest.skip(f"skipping {sch_path} due to: {e}")

    assert isinstance(sch, Schematic)

    tmp_dir = tmp_path_factory.mktemp("kicad_files")
    tmp_net_kicad = tmp_dir / "test_kicad.net"
    process_kicad = subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", sch_path, "-o", tmp_net_kicad],
        capture_output=True,
    )
    contents = to_str(sch)
    tmp_sch = tmp_dir / "test_edea.kicad_sch"
    with open(tmp_sch, "w") as f:
        f.write(contents)
    tmp_net_edea = tmp_dir / "test_edea.net"
    process = subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", tmp_sch, "-o", tmp_net_edea],
        capture_output=True,
    )
    assert (
        process.stderr == b""
        # kicad-cli lock file errors happen when we run tests in parallel but
        # don't affect anything we are doing
        or b"Invalid lock file" in process.stderr
        or b"Failed to access lock" in process.stderr
        or b"Failed to inspect the lock file " in process.stderr
    ), (
        f"got output on stderr: {process.stderr}\n"
        f"when trying to read: '{str(tmp_sch)}'\n"
        f"generated from: '{str(sch_path)}'"
    )
    assert process.stdout == b"" or process.stdout == process_kicad.stdout, (
        f"unexpected output on stdout: {process.stdout}\n"
        f"expecting: {process_kicad.stdout}\n"
        f"when trying to read: '{str(tmp_sch)}'\n"
        f"generated from: '{str(sch_path)}'"
    )
    assert process.returncode == 0, (
        f"failed trying to read: '{str(tmp_sch)}'\n"
        f"generated from: '{str(sch_path)}'"
    )
