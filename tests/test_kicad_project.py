import json

from edea.kicad.project import KicadProject


def test_kicad_project_load_one_MP2451():
    file_name = "tests/kicad_projects/MP2451/MP2451.kicad_pro"
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
    project = KicadProject(**data)
    assert project is not None


def test_kicad_project_load_one_ferret():
    file_name = "tests/kicad_projects/ferret/ferret.kicad_pro"
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
    project = KicadProject(**data)
    assert project is not None
