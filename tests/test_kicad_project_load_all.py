"""
Test that parses as many .kicad_pro as we could find.

SPDX-License-Identifier: EUPL-1.2
"""

import json
import os

import pytest

from edea.kicad.project import KicadProject

test_folder = os.path.dirname(os.path.realpath(__file__))
kicad_folder = os.path.join(test_folder, "kicad_projects/kicad-test-files")


kicad_pro_files = []
for root, dirs, files in os.walk(kicad_folder):
    for file in files:
        path = os.path.join(root, file)
        if file.endswith(".kicad_pro"):
            kicad_pro_files.append(path)


@pytest.mark.parametrize("pro_path", kicad_pro_files)
def test_load_all_kicad_pro(pro_path):
    with open(pro_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    project = KicadProject(**data)
    assert project is not None
