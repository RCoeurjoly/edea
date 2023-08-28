from json import loads

from edea.types.project import Project


def test_project_metadata():
    project_file = "tests/kicad_projects/leako/ColecoVision Clone.kicad_pro"
    project_metadata_fixture = {
        "area_mm": 15213.841,
        "width_mm": 151.638,
        "height_mm": 100.33,
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
