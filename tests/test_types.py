from edea.types.parser import from_str
from edea.types.schematic import Schematic
from edea.types.pcb import Pcb

file_name = "tests/kicad_projects/MP2451/MP2451"
class TestTypes:
    def test_schematic(self):
        with open(
            f"{file_name}.kicad_sch", encoding="utf-8"
        ) as f:
            sch = from_str(f.read())

        assert isinstance(sch, Schematic)

    def test_pcb(self):
        with open(
            f"{file_name}.kicad_pcb", encoding="utf-8"
        ) as f:
            pcb = from_str(f.read())

        assert isinstance(pcb, Pcb)
