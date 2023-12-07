from edea.kicad.parser import from_str
from edea.kicad.pcb import Pcb
from edea.kicad.schematic import Schematic

file_name = "tests/kicad_projects/MP2451/MP2451"


def test_parse_one_schematic():
    with open(f"{file_name}.kicad_sch", encoding="utf-8") as f:
        sch = from_str(f.read())

    assert isinstance(sch, Schematic)


def test_parse_one_pcb():
    with open(f"{file_name}.kicad_pcb", encoding="utf-8") as f:
        pcb = from_str(f.read())

    assert isinstance(pcb, Pcb)
