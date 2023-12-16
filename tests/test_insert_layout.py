import pathlib

from edea.kicad.parser import parse_pcb
from edea.kicad.pcb import Pcb
from edea.kicad.serializer import to_str

from ._kicad_cli import kicad_cli


def test_insert_layout_basic():
    a = Pcb()
    b = Pcb()
    b.insert_layout("test", a)
    assert b is not None


def test_insert_layout_from_file(tmp_path: pathlib.Path):
    mp2451_path = "tests/kicad_projects/MP2451/MP2451.kicad_pcb"
    with open(mp2451_path, encoding="utf-8") as f:
        mp2451 = parse_pcb(f.read())

    ferret_path = "tests/kicad_projects/ferret/ferret.kicad_pcb"
    with open(ferret_path, encoding="utf-8") as f:
        ferret = parse_pcb(f.read())

    ferret.insert_layout("MP2451", mp2451)

    test_path = tmp_path / "test.kicad_pcb"
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(to_str(ferret))

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
