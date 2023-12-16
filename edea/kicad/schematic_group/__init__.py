import os
import pathlib
from dataclasses import dataclass

from edea._utils import remove_ref_number
from edea.kicad.parser import parse_schematic
from edea.kicad.schematic import (
    Schematic,
    Sheet,
    SheetInstancesPath,
    SubSheetInstanceProject,
    SubSheetInstances,
)
from edea.kicad.serializer import to_str


@dataclass
class SchematicFile:
    filepath: pathlib.Path
    data: Schematic


class SchematicGroup:
    folder: pathlib.Path
    top_level: SchematicFile
    sub_schematics: list[SchematicFile]

    def __init__(self, path: pathlib.Path | str):
        if isinstance(path, str):
            path = pathlib.Path(path)
        absolute_path = path.absolute()
        with open(absolute_path, "r", encoding="utf-8") as f:
            sch = parse_schematic(f.read())
        self.folder = absolute_path.parent
        filepath = absolute_path.relative_to(self.folder)
        self.top_level = SchematicFile(filepath=filepath, data=sch)

        self.sub_schematics = []

        for sheet in self.top_level.data.sheets:
            filepath = pathlib.Path(sheet.file)
            absolute_path = self.folder / filepath
            with open(absolute_path, "r", encoding="utf-8") as f:
                sch = parse_schematic(f.read())

            self.sub_schematics.append(SchematicFile(filepath=filepath, data=sch))

    def add_sub_schematic(self, filepath: pathlib.Path | str, sch: Schematic):
        if isinstance(filepath, str):
            filepath = pathlib.Path(filepath)

        page_number = 0
        for sheet in self.top_level.data.sheets:
            if sheet.instances is not None:
                try:
                    n = sheet.instances.projects[0].paths[0].page
                    page_number = max(page_number, int(n))
                except (IndexError, ValueError):
                    pass

        uuid = self.top_level.data.uuid
        project_name = self.top_level.filepath.stem
        sheet = Sheet(
            name=filepath.stem,
            file=filepath,
            instances=SubSheetInstances(
                projects=[
                    SubSheetInstanceProject(
                        name=project_name,
                        paths=[
                            SheetInstancesPath(
                                name=f"/{uuid}", page=str(page_number + 1)
                            )
                        ],
                    )
                ]
            ),
        )
        self.top_level.data.sheets.append(sheet)

        for symbol in sch.symbols:
            # remove symbol instances, these are links to the top level schematic.
            # if we remove them then kicad will add a correct one when it opens the
            # project
            symbol.instances = None
            # remove the numbers from reference designators so kicad can re-assign them
            symbol.reference = remove_ref_number(symbol.reference)

        self.sub_schematics.append(SchematicFile(filepath=filepath, data=sch))

    def write_to_disk(self):
        top_str = to_str(self.top_level.data)

        os.makedirs(self.folder, exist_ok=True)
        with open(self.folder / self.top_level.filepath, "w", encoding="utf-8") as f:
            f.write(top_str)

        for sub in self.sub_schematics:
            sub_str = to_str(sub.data)
            sub_path = self.folder / sub.filepath
            sub_folder = sub_path.parent
            os.makedirs(sub_folder, exist_ok=True)
            with open(sub_path, "w", encoding="utf-8") as f:
                f.write(sub_str)
