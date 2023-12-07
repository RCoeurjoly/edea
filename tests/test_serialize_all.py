"""
Test that parses then serializes as many KiCad schematic and PCB files as we
could find.

SPDX-License-Identifier: EUPL-1.2
"""

import os
import shutil
import subprocess

import pytest

from edea.kicad.common import VersionError
from edea.kicad.parser import from_str
from edea.kicad.pcb import Pcb
from edea.kicad.schematic import Schematic
from edea.kicad.serializer import to_str

test_folder = os.path.dirname(os.path.realpath(__file__))
kicad_folder = os.path.join(test_folder, "kicad_projects/kicad-test-files")

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

    kicad_stderr = [
        line
        for line in process_kicad.stderr.split(b"\n")
        if
        # kicad-cli lock file errors happen when we run tests in parallel but
        # don't affect anything we are doing
        line != b""
        and b"Invalid lock file" not in line
        and b"Failed to access lock" not in line
        and b"Failed to inspect the lock file" not in line
    ]

    # skip files that already have warnings/errors
    if process_kicad.returncode != 0 or kicad_stderr != []:
        return pytest.skip()

    contents = to_str(sch)
    tmp_sch = tmp_dir / "test_edea.kicad_sch"
    with open(tmp_sch, "w") as f:
        f.write(contents)
    tmp_net_edea = tmp_dir / "test_edea.net"
    process = subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", tmp_sch, "-o", tmp_net_edea],
        capture_output=True,
    )

    test_stderr = [
        line
        for line in process.stderr.split(b"\n")
        if
        # kicad-cli lock file errors happen when we run tests in parallel but
        # don't affect anything we are doing
        line != b""
        and b"Invalid lock file" not in line
        and b"Failed to access lock" not in line
        and b"Failed to inspect the lock file" not in line
    ]

    assert len(test_stderr) == 0, (
        f"got output on stderr: {[s.decode('utf8') for s in test_stderr]}\n"
        f"when trying to read: '{str(tmp_sch)}'\n"
        f"generated from: '{str(sch_path)}'"
    )
    assert process.stdout == b"" or process.stdout == process_kicad.stdout, (
        f"unexpected output on stdout: {process.stdout.decode('utf8')}\n"
        f"expecting: {process_kicad.stdout}\n"
        f"when trying to read: '{str(tmp_sch)}'\n"
        f"generated from: '{str(sch_path)}'"
    )
    assert process.returncode == 0, (
        f"failed trying to read: '{str(tmp_sch)}'\n"
        f"generated from: '{str(sch_path)}'"
    )

    # to make sure we don't run out of space
    shutil.rmtree(tmp_dir)


@pytest.mark.parametrize("pcb_path", kicad_pcb_files)
def test_serialize_all_pcb_files(pcb_path, tmp_path_factory):
    with open(pcb_path, encoding="utf-8") as f:
        try:
            pcb = from_str(f.read())
        except (VersionError, EOFError) as e:
            return pytest.skip(f"skipping {pcb_path} due to: {e}")

    assert isinstance(pcb, Pcb)

    tmp_dir = tmp_path_factory.mktemp("kicad_files")
    tmp_svg_kicad = tmp_dir / "test_pcb_kicad.svg"
    process_kicad = subprocess.run(
        [
            "kicad-cli",
            "pcb",
            "export",
            "svg",
            "--layers=*",
            pcb_path,
            "-o",
            tmp_svg_kicad,
        ],
        capture_output=True,
    )

    kicad_stderr = [
        line
        for line in process_kicad.stderr.split(b"\n")
        if
        # kicad-cli lock file errors happen when we run tests in parallel but
        # don't affect anything we are doing
        line != b""
        and b"Invalid lock file" not in line
        and b"Failed to access lock" not in line
        and b"Failed to inspect the lock file" not in line
    ]

    # skip files that already have warnings/errors
    if process_kicad.returncode != 0 or kicad_stderr != []:
        return pytest.skip()

    contents = to_str(pcb)
    tmp_pcb = tmp_dir / "test_edea.kicad_pcb"
    with open(tmp_pcb, "w") as f:
        f.write(contents)
    tmp_svg_edea = tmp_dir / "test_pcb_edea.svg"
    process = subprocess.run(
        [
            "kicad-cli",
            "pcb",
            "export",
            "svg",
            "--layers=*",
            tmp_pcb,
            "-o",
            tmp_svg_edea,
        ],
        capture_output=True,
    )

    test_stderr = [
        line
        for line in process.stderr.split(b"\n")
        if
        # kicad-cli lock file errors happen when we run tests in parallel but
        # don't affect anything we are doing
        line != b""
        and b"Invalid lock file" not in line
        and b"Failed to access lock" not in line
        and b"Failed to inspect the lock file" not in line
    ]

    assert len(test_stderr) == 0, (
        f"got output on stderr: {[s.decode('utf8') for s in test_stderr]}\n"
        f"when trying to read: '{str(tmp_pcb)}'\n"
        f"generated from: '{str(pcb_path)}'"
    )
    assert process.stdout == b"" or process.stdout == process_kicad.stdout, (
        f"unexpected output on stdout: {process.stdout.decode('utf8')}\n"
        f"expecting: {process_kicad.stdout}\n"
        f"when trying to read: '{str(tmp_pcb)}'\n"
        f"generated from: '{str(pcb_path)}'"
    )
    assert process.returncode == 0, (
        f"failed trying to read: '{str(tmp_pcb)}'\n"
        f"generated from: '{str(pcb_path)}'"
    )

    # to make sure we don't run out of space
    shutil.rmtree(tmp_dir)
