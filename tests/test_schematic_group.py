import pathlib
import shutil
from uuid import UUID, uuid4

import pytest

from edea.kicad.parser import load_schematic
from edea.kicad.schematic import Schematic, SymbolUse, SymbolUseInstances
from edea.kicad.schematic_group import SchematicGroup

file_name = "tests/kicad_projects/schematic_group/schematic_group.kicad_sch"


def test_sch_group_create():
    group = SchematicGroup(Schematic(), "test.kicad_sch")
    assert len(group._top_level.data.sheets) == 0


def test_sch_group_add_sub_uuid():
    group = SchematicGroup(Schematic(), "test.kicad_sch")
    uuid = group.add_sub_schematic(Schematic(), output_path="test2.kicad_sch")
    assert isinstance(uuid, UUID)


def test_sch_group_load_from_disk():
    group = SchematicGroup.load_from_disk(file_name)
    assert len(group._top_level.data.sheets) == 1


def test_sch_group_add_sub():
    group = SchematicGroup.load_from_disk(file_name)
    group.add_sub_schematic(Schematic(), output_path="test.kicad_sch")
    assert len(group._top_level.data.sheets) == 2


def test_sch_group_add_sub_same_name():
    group = SchematicGroup(Schematic(), "test.kicad_sch")
    with pytest.raises(ValueError):
        group.add_sub_schematic(Schematic(), output_path="test.kicad_sch")


def test_sch_group_add_sub_same_name2():
    group = SchematicGroup(Schematic(), "test.kicad_sch")
    group.add_sub_schematic(Schematic(), output_path="test2.kicad_sch")
    with pytest.raises(ValueError):
        group.add_sub_schematic(Schematic(), output_path="test2.kicad_sch")


def test_sch_group_add_sub_bad_paths1():
    group = SchematicGroup(Schematic(), "test.kicad_sch")
    with pytest.raises(ValueError):
        group.add_sub_schematic(Schematic(), output_path="../bad.kicad_sch")


def test_sch_group_add_sub_bad_paths2():
    group = SchematicGroup(Schematic(), "test.kicad_sch")
    with pytest.raises(ValueError):
        group.add_sub_schematic(Schematic(), output_path="./../bad.kicad_sch")


def test_sch_group_add_sub_bad_paths3():
    group = SchematicGroup(Schematic(), "test.kicad_sch")
    with pytest.raises(ValueError):
        group.add_sub_schematic(Schematic(), output_path="hello/../../bad.kicad_sch")


def test_sch_group_add_sub_bad_paths4():
    group = SchematicGroup.load_from_disk(file_name)
    with pytest.raises(ValueError):
        group.add_sub_schematic(Schematic(), output_path="/root")


def test_sch_group_add_sub_removes_instances():
    """
    Test that we remove symbol instances. these are links to the top level
    schematic. if we remove them then kicad will add a correct one when it
    opens the project
    """
    group = SchematicGroup.load_from_disk(file_name)
    test_sch = Schematic(
        symbols=[SymbolUse(reference="R1", value="1k", instances=SymbolUseInstances())]
    )
    assert test_sch.symbols[0].instances is not None
    group.add_sub_schematic(test_sch, output_path="test.kicad_sch")
    test_sch = group._added_sub_schematics[0].data
    assert test_sch.symbols[0].instances is None


def test_sch_group_add_sub_removes_ref_numbers():
    """
    Test that we remove the numbers from schematic reference designators
    """
    group = SchematicGroup.load_from_disk(file_name)
    test_sch = Schematic(symbols=[SymbolUse(reference="R1", value="1k")])
    assert test_sch.symbols[0].reference == "R1"
    group.add_sub_schematic(test_sch, output_path="test.kicad_sch")
    test_sch = group._added_sub_schematics[0].data
    assert test_sch.symbols[0].reference == "R"


def test_sch_group_write(tmp_path: pathlib.Path):
    top_filepath = pathlib.Path(file_name)
    tmp_top_filepath = tmp_path / top_filepath.name
    shutil.copy(top_filepath, tmp_top_filepath)

    sub_filepath = top_filepath.parent / "sub_sheet_1.kicad_sch"
    tmp_sub_filepath = tmp_path / sub_filepath.name
    shutil.copy(sub_filepath, tmp_sub_filepath)

    group = SchematicGroup.load_from_disk(tmp_top_filepath)
    test_sch_1 = Schematic(uuid=uuid4())
    group.add_sub_schematic(test_sch_1, output_path="test.kicad_sch")
    group.write_to_disk(tmp_path)

    test_filepath = tmp_path / "test.kicad_sch"
    test_sch_2 = load_schematic(test_filepath)
    assert test_sch_2 == test_sch_1


def test_sch_group_write_folder(tmp_path: pathlib.Path):
    top_filepath = pathlib.Path(file_name)
    tmp_top_filepath = tmp_path / top_filepath.name
    shutil.copy(top_filepath, tmp_top_filepath)

    sub_filepath = top_filepath.parent / "sub_sheet_1.kicad_sch"
    tmp_sub_filepath = tmp_path / sub_filepath.name
    shutil.copy(sub_filepath, tmp_sub_filepath)

    group = SchematicGroup.load_from_disk(tmp_top_filepath)
    test_sch_1 = Schematic(uuid=uuid4())
    group.add_sub_schematic(test_sch_1, output_path="folder/test.kicad_sch")
    group.write_to_disk(tmp_path)

    test_filepath = tmp_path / "folder/test.kicad_sch"
    test_sch_2 = load_schematic(test_filepath)
    assert test_sch_2 == test_sch_1
