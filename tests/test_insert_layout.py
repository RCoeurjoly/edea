import pathlib

from edea.kicad._kicad_cli import kicad_cli
from edea.kicad.parser import load_pcb
from edea.kicad.pcb import Pcb
from edea.kicad.serializer import write_pcb


def test_insert_layout_basic():
    a = Pcb()
    b = Pcb()
    b.insert_layout("test", a)
    assert b is not None


def test_insert_layout_from_file(tmp_path: pathlib.Path):
    mp2451_path = "tests/kicad_projects/MP2451/MP2451.kicad_pcb"
    mp2451 = load_pcb(mp2451_path)

    ferret_path = "tests/kicad_projects/ferret/ferret.kicad_pcb"
    ferret = load_pcb(ferret_path)

    ferret.insert_layout("MP2451", mp2451)

    test_path = tmp_path / "test.kicad_pcb"
    write_pcb(test_path, ferret)

    tmp_svg = tmp_path / "test.svg"
    process = kicad_cli(
        [
            "pcb",
            "export",
            "svg",
            "--layers=*",
            test_path,
            "-o",
            tmp_svg,
        ]
    )
    assert process.returncode == 0
