"EDeA module metadata."

import itertools
from functools import cached_property
from typing import cast
from warnings import warn

from pydantic import BaseModel

from edea.kicad.parser import from_str
from edea.kicad.pcb import Pcb
from edea.kicad.schematic import Schematic


class EdeaModuleMetadata(BaseModel):
    """
    Metadata for the EDeA module.

    :param area_mm: The area of the module in millimeters.
    :param width_mm: The width of the module in millimeters.
    :param height_mm: The height of the module in millimeters.
    :param count_copper_layer: The number of copper layers in the module schematic.
    :param sheets: The number of sheets in the module schematic.
    :param count_part: The total number of parts in the module.
    :param count_unique_part: The number of unique parts in the module.
    :param parts: Detailed information about the parts in the module.
    """

    area_mm: float | None = None
    width_mm: float | None = None
    height_mm: float | None = None
    count_copper_layer: int | None = None
    sheets: int | None = None
    count_part: int | None = None
    count_unique_part: int | None = None
    parts: dict[str, dict[str, str]] = {}


class Project:
    """
    A convenience wrapper for loading kicad project files. Provides metadata about the project.

    :param path: The path of the `kicad_pro`.

    :raises ValueError: If the provided path doesn't end with the '.kicad_pro' extension.
    """

    def __init__(self, path: str):
        if not path.endswith(".kicad_pro"):
            raise ValueError("KiCad project file must end with .kicad_pro")

        self.path = path
        sch_path = path.replace(".kicad_pro", ".kicad_sch")
        pcb_path = path.replace(".kicad_pro", ".kicad_pcb")

        with open(sch_path, encoding="utf-8") as sf, open(
            pcb_path, encoding="utf-8"
        ) as pf:
            self.schematic = cast(Schematic, from_str(sf.read()))
            self.pcb = cast(Pcb, from_str(pf.read()))

    @cached_property
    def metadata(self):
        """
        Project metadata.

        :returns: Moduel's area, width, height, number of copper layers, number \
            of sheets, number of parts, number of unique parts, and detailed information about the parts.

        :raises Warning: If it couldn't calculate the board size.

        """
        data = EdeaModuleMetadata()

        for symbol in self.schematic.symbols:
            if any(
                # skip virtual symbols (e.g., gnd)
                property.key == "Reference" and property.value.startswith("#")
                for property in symbol.properties
            ):
                continue

            data.parts[str(symbol.uuid)] = {
                property.key: property.value for property in symbol.properties
            }

        data.sheets = len(self.schematic.sheets)
        data.count_part = len(data.parts)
        data.count_unique_part = self._count_unique_part(data.parts)

        copper_layers = [layer for layer in self.pcb.layers if layer[1] == "F.Cu"]
        data.count_copper_layer = len(copper_layers)

        try:
            board_size = self.pcb.size()
        except ValueError:
            warn("Could not calculate board size.")
        else:
            data.height_mm = round(board_size.height_mm, 3)
            data.width_mm = round(board_size.width_mm, 3)
            data.area_mm = round(data.height_mm * data.width_mm, 3)

        return data

    def _count_unique_part(self, parts: dict[str, dict[str, str]]) -> int:
        """
        Calculates the number of unique parts within the project.

        :param parts: Detailed information about the parts within the project.

        :returns: The number of unique parts within the project.
        """
        return len(
            list(
                itertools.groupby(
                    # groupby only works with consecutive keys
                    sorted(parts.values(), key=Project._count_unique_part_key),
                    Project._count_unique_part_key,
                )
            )
        )

    @staticmethod
    def _count_unique_part_key(part: dict[str, str]) -> str:
        """
        Defines the key used for grouping unique parts in the project to identify unique instances.

        :param part: Detailed information about the part.

        :returns: The key used for grouping unique parts.
        """
        if mpn := part.get("MPN"):
            return mpn
        if lcsc := part.get("LCSC"):
            return lcsc

        return f"{part['Value']} {part['Footprint']}"
