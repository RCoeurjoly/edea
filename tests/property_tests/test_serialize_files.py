import os

import pytest
from hypothesis import given, infer

from edea.kicad.schematic import Schematic
from edea.kicad.serializer import to_str


@pytest.mark.skip(
    "Cannot yet create arbitrary schematic files that KiCad is guaranteed to be "
    "able to read."
)
@given(expr=infer)
def test_serialize_any_sch_files(expr: Schematic, tmp_path_factory):
    """
    Test that serializing any arbitrary `Schematic` is openable by KiCad.
    """
    contents = to_str(expr)
    tmp_dir = tmp_path_factory.mktemp("kicad_files")
    tmp_sch = tmp_dir / "x.kicad_sch"
    with open(tmp_sch, "w") as f:
        f.write(contents)
    tmp_net = tmp_dir / "x.net"
    exit_code = os.system(f"kicad-cli sch export netlist '{tmp_sch}' -o '{tmp_net}'")
    assert exit_code == 0, f"failed trying to read: '{str(tmp_sch)}'"
