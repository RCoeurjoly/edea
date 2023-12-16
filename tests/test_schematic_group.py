import pathlib
import shutil

from edea.kicad.parser import parse_schematic
from edea.kicad.schematic import Schematic, SymbolUse, SymbolUseInstances
from edea.kicad.schematic_group import SchematicGroup

file_name = "tests/kicad_projects/schematic_group/schematic_group.kicad_sch"


def test_sch_group_create():
    group = SchematicGroup(file_name)
    assert len(group.sub_schematics) == 1
    assert len(group.top_level.data.sheets) == 1


def test_sch_group_add_sub():
    group = SchematicGroup(file_name)
    group.add_sub_schematic("test.kicad_sch", Schematic())
    assert len(group.sub_schematics) == 2
    assert len(group.top_level.data.sheets) == 2


def test_sch_group_add_sub_removes_instances():
    """
    Test that we remove symbol instances. these are links to the top level
    schematic. if we remove them then kicad will add a correct one when it
    opens the project
    """
    group = SchematicGroup(file_name)
    test_sch = Schematic(
        symbols=[SymbolUse(reference="R1", value="1k", instances=SymbolUseInstances())]
    )
    assert test_sch.symbols[0].instances is not None
    group.add_sub_schematic("test.kicad_sch", test_sch)
    test_sch = group.sub_schematics[1].data
    assert test_sch.symbols[0].instances is None


def test_sch_group_add_sub_removes_ref_numbers():
    """
    Test that we remove the numbers from schematic reference designators
    """
    group = SchematicGroup(file_name)
    test_sch = Schematic(symbols=[SymbolUse(reference="R1", value="1k")])
    assert test_sch.symbols[0].reference == "R1"
    group.add_sub_schematic("test.kicad_sch", test_sch)
    test_sch = group.sub_schematics[1].data
    assert test_sch.symbols[0].reference == "R"


def test_sch_group_write(tmp_path: pathlib.Path):
    top_filepath = pathlib.Path(file_name)
    tmp_top_filepath = tmp_path / top_filepath.name
    shutil.copy(top_filepath, tmp_top_filepath)

    sub_filepath = top_filepath.parent / "sub_sheet_1.kicad_sch"
    tmp_sub_filepath = tmp_path / sub_filepath.name
    shutil.copy(sub_filepath, tmp_sub_filepath)

    group = SchematicGroup(tmp_top_filepath)
    test_sch_1 = Schematic()
    group.add_sub_schematic("test.kicad_sch", test_sch_1)
    group.write_to_disk()

    test_filepath = tmp_path / "test.kicad_sch"

    with open(test_filepath, "r", encoding="utf-8") as f:
        test_contents = f.read()

    test_sch_2 = parse_schematic(test_contents)

    assert test_sch_2 == test_sch_1


def test_sch_group_write_folder(tmp_path: pathlib.Path):
    top_filepath = pathlib.Path(file_name)
    tmp_top_filepath = tmp_path / top_filepath.name
    shutil.copy(top_filepath, tmp_top_filepath)

    sub_filepath = top_filepath.parent / "sub_sheet_1.kicad_sch"
    tmp_sub_filepath = tmp_path / sub_filepath.name
    shutil.copy(sub_filepath, tmp_sub_filepath)

    group = SchematicGroup(tmp_top_filepath)
    test_sch_1 = Schematic()
    group.add_sub_schematic("folder/test.kicad_sch", test_sch_1)
    group.write_to_disk()

    test_filepath = tmp_path / "folder/test.kicad_sch"

    with open(test_filepath, "r", encoding="utf-8") as f:
        test_contents = f.read()

    test_sch_2 = parse_schematic(test_contents)

    assert test_sch_2 == test_sch_1
