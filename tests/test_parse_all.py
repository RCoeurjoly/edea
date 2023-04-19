"""
Test that parses as many KiCad 6 projects as we could find.

SPDX-License-Identifier: EUPL-1.2
"""

import os
import re
import pytest


from edea.edea import Project, VersionError as OriginalVersionError
from edea.types.parser import from_str
from edea.types.schematic import Schematic
from edea.types.pcb import Pcb
from edea.types.common import VersionError

test_folder = os.path.dirname(os.path.realpath(__file__))
kicad_folder = os.path.join(test_folder, "kicad_projects/kicad6-test-files")

kicad_pcb_files = []
for root, dirs, files in os.walk(kicad_folder):
    for file in files:
        if file.endswith(".kicad_pcb"):
            path = os.path.join(root, file)
            kicad_pcb_files.append(path)

kicad_projects = [
    (re.sub(r"\.kicad_pcb$", ".kicad_sch", pcb_path), pcb_path)
    for pcb_path in kicad_pcb_files
]


@pytest.mark.parametrize("kicad_file_pair", kicad_projects)
def test_parse_all(kicad_file_pair):
    sch_path, pcb_path = kicad_file_pair
    pro = Project(sch_path, pcb_path)
    try:
        pro.parse()
    except OriginalVersionError as e:
        print(f"skipping {sch_path} due to old format: {e}")
    except FileNotFoundError:
        print(f"project {sch_path} appears to be incomplete")
    except AttributeError as e:
        # some minimal files don't have a uuid, but they're not interesting anyway.
        if "uuid" in str(e):
            print(f"{sch_path} does not contain a uuid")
        else:
            raise e
    except EOFError:
        print(f"{sch_path} contains unmatched braces or there's a parser error")
    except Exception as e:
        print(f"failed to parse {sch_path}")
        raise e


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
def test_parse_all_types(sch_path):
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
