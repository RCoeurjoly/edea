"""
Test that parses as many KiCad 6 projects as we could find.

SPDX-License-Identifier: EUPL-1.2
"""

import os
import pytest


from edea.types.parser import from_str
from edea.types.schematic import Schematic
from edea.types.pcb import Pcb
from edea.types.common import VersionError

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
def test_parse_all_sch(sch_path):
    with open(sch_path, encoding="utf-8") as f:
        try:
            sch = from_str(f.read())
        except VersionError as e:
            pytest.skip(f"skipping {sch_path} due to: {e}")
        except EOFError as e:
            pytest.skip(f"skipping {sch_path} due to: {e}")
        else:
            assert isinstance(sch, Schematic)


@pytest.mark.parametrize("pcb_path", kicad_pcb_files)
def test_parse_all_pcb(pcb_path):
    with open(pcb_path, encoding="utf-8") as f:
        try:
            pcb = from_str(f.read())
        except VersionError as e:
            pytest.skip(f"skipping {pcb_path} due to: {e}")
        except EOFError as e:
            pytest.skip(f"skipping {pcb_path} due to: {e}")
        else:
            assert isinstance(pcb, Pcb)
