from json import loads

from edea.kicad.project import Project


def test_project_metadata():
    project_file = "tests/kicad_projects/leako/ColecoVision Clone.kicad_pro"
    project_metadata_fixture = {
        "area_mm": 14732.571,
        "width_mm": 149.1,
        "height_mm": 98.81,
        "count_copper_layer": 1,
        "sheets": 5,
        "count_part": 19,
        "count_unique_part": 11,
    }

    project = Project(project_file)
    metadata = loads(
        project.metadata.json(
            # parts are tested via the count other wise the fixture would be too big
            exclude={"parts"}
        )
    )
    assert metadata == project_metadata_fixture
