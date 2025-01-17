import os
import pathlib
from dataclasses import dataclass
from uuid import UUID

from edea._utils import remove_ref_number
from edea.kicad.parser import load_schematic
from edea.kicad.schematic import (
    Schematic,
    Sheet,
    SheetInstancesPath,
    SubSheetInstanceProject,
    SubSheetInstances,
)
from edea.kicad.serializer import write_schematic


@dataclass
class SchematicFile:
    filepath: pathlib.Path
    data: Schematic


class SchematicGroup:
    _top_level: SchematicFile
    _added_sub_schematics: list[SchematicFile]

    def __init__(self, top_level: Schematic, top_level_filename: pathlib.Path | str):
        if not isinstance(top_level_filename, pathlib.Path):
            top_level_filename = pathlib.Path(top_level_filename)
        _check_path(top_level_filename)
        self._added_sub_schematics = []
        self._top_level = SchematicFile(filepath=top_level_filename, data=top_level)

    @classmethod
    def load_from_disk(cls, top_level: pathlib.Path | str) -> "SchematicGroup":
        if not isinstance(top_level, pathlib.Path):
            top_level = pathlib.Path(top_level)
        sch = load_schematic(top_level)
        filename = pathlib.Path(top_level.name)
        self = cls(sch, filename)
        return self

    def add_sub_schematic(
        self,
        sch: Schematic,
        output_path: pathlib.Path | str,
    ) -> UUID:
        if isinstance(output_path, str):
            output_path = pathlib.Path(output_path)

        _check_path(output_path)

        if output_path == self._top_level.filepath or output_path in (
            s.filepath for s in self._added_sub_schematics
        ):
            raise ValueError("File already exists in schematic group.")

        page_number = 0
        for sheet in self._top_level.data.sheets:
            if sheet.instances is not None:
                try:
                    n = sheet.instances.projects[0].paths[0].page
                    page_number = max(page_number, int(n))
                except (IndexError, ValueError):
                    # we just ignore it when there are no existing
                    # sub-schematics (sheet.instances.projects), i.e.
                    # IndexError, or when the "page" is not a number, i.e.
                    # ValueError
                    pass

        uuid = self._top_level.data.uuid
        project_name = self._top_level.filepath.stem
        sheet = Sheet(
            name=output_path.stem,
            file=output_path,
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
        self._top_level.data.sheets.append(sheet)

        for symbol in sch.symbols:
            # remove symbol instances, these are links to the top level schematic.
            # if we remove them then kicad will add a correct one when it opens the
            # project
            symbol.instances = None
            # remove the numbers from reference designators so kicad can re-assign them
            symbol.reference = remove_ref_number(symbol.reference)

        self._added_sub_schematics.append(SchematicFile(filepath=output_path, data=sch))

        return sheet.uuid

    def write_to_disk(self, output_folder: pathlib.Path | str):
        if not isinstance(output_folder, pathlib.Path):
            output_folder = pathlib.Path(output_folder)

        os.makedirs(output_folder, exist_ok=True)
        write_schematic(output_folder / self._top_level.filepath, self._top_level.data)

        for sub in self._added_sub_schematics:
            sub_path = output_folder / sub.filepath
            sub_folder = sub_path.parent
            os.makedirs(sub_folder, exist_ok=True)
            write_schematic(sub_path, sub.data)


def _check_path(path: pathlib.Path):
    if ".." in path.parts:
        raise ValueError(f"Path must be in the current directory, got: {path}")
    if path.is_absolute():
        raise ValueError(
            "Given an absolute path, path must be relative to the current directory."
        )
