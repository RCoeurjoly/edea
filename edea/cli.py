"""
edea command line tool

SPDX-License-Identifier: EUPL-1.2
"""
import os
import pathlib

import rich
import typer
import typer.rich_utils
from click import UsageError
from pydantic import ValidationError
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn

from edea.kicad.common import VersionError
from edea.kicad.parser import load_pcb, load_schematic
from edea.kicad.pcb import Pcb
from edea.kicad.schematic_group import SchematicGroup
from edea.kicad.serializer import write_pcb

# https://github.com/tiangolo/typer/issues/437
typer.rich_utils.STYLE_HELPTEXT = ""

cli = typer.Typer(
    rich_markup_mode="rich",
    # disabled for now till we have more commands and options
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@cli.callback()
def cli_root():
    """
    edea add ../example/
    """


@cli.command()
def add(
    module_directory: pathlib.Path,
):
    """

    Add an edea module to your current project.

    \b
    edea add ../example/

    """
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        transient=True,
    ) as progress:
        adding_task = progress.add_task(f"Adding {module_directory}", total=100)
        project_files = os.listdir(".")
        project_pcb_path = None
        for file in project_files:
            if file.endswith(".kicad_pcb"):
                project_pcb_path = pathlib.Path(file)
                break
        if project_pcb_path is None:
            raise UsageError(
                "No KiCad PCB file (.kicad_pcb) found in the current directory."
                " Please use edea from a project directory.",
            )
        project_sch_path = project_pcb_path.with_suffix(".kicad_sch")
        if not project_sch_path.exists():
            raise UsageError(
                f"No KiCad schematic file ('{project_sch_path}') found in the current"
                " directory.",
            )

        module_files = os.listdir(module_directory)
        module_pcb_path = None
        for file in module_files:
            if file.endswith(".kicad_pcb"):
                module_pcb_path = module_directory / file
                break
        if module_pcb_path is None:
            raise UsageError(
                "No KiCad PCB file (.kicad_pcb) found in the module directory.",
            )
        module_sch_path = module_pcb_path.with_suffix(".kicad_sch")
        if not module_sch_path.exists():
            raise UsageError(
                f"No KiCad schematic file ('{module_sch_path}')"
                " found in the module directory.",
            )

        progress.update(adding_task, completed=3)

        try:
            schematic_group = SchematicGroup.load_from_disk(top_level=project_sch_path)
        except (VersionError, ValidationError, TypeError, ValueError) as e:
            raise UsageError(f"Could not parse {project_sch_path}: {e}") from e

        progress.update(adding_task, completed=6)

        try:
            module_sch = load_schematic(module_sch_path)
        except (VersionError, ValidationError, TypeError, ValueError) as e:
            raise UsageError(f"Could not parse {module_sch_path}: {e}") from e

        progress.update(adding_task, completed=21)

        try:
            project_pcb: Pcb = load_pcb(project_pcb_path)
        except (VersionError, ValidationError, TypeError, ValueError) as e:
            raise UsageError(f"Could not parse {project_pcb_path}: {e}") from e

        progress.update(adding_task, completed=33)

        try:
            module_pcb = load_pcb(module_pcb_path)
        except (VersionError, ValidationError, TypeError, ValueError) as e:
            raise UsageError(f"Could not parse {module_pcb_path}: {e}") from e

        progress.update(adding_task, completed=67)

        module_name = module_pcb_path.stem
        sch_output_path = f"edea_schematics/{module_name}/{module_name}.kicad_sch"
        sub_schematic_uuid = schematic_group.add_sub_schematic(
            module_sch, output_path=sch_output_path
        )
        project_pcb.insert_layout(
            module_name, module_pcb, uuid_prefix=sub_schematic_uuid
        )

        progress.update(adding_task, completed=82)

        schematic_group.write_to_disk(output_folder=project_sch_path.parent)
        write_pcb(project_pcb_path, project_pcb)

        progress.update(adding_task, completed=100)

        rich.print(
            f":sparkles: [green]Successfully added"
            f" [bright_cyan]{module_directory}[/bright_cyan] to"
            f" [bright_magenta]{project_pcb_path.stem}[/bright_magenta] :sparkles:"
        )
        rich.print(
            Panel.fit(
                f"- Sub-schematic was created at"
                f" [bright_cyan]{sch_output_path}[/bright_cyan] and added to"
                f" [bright_magenta]{project_sch_path.stem}[/bright_magenta][bright_cyan].kicad_sch[/bright_cyan]\n"
                f"- Layout was merged into"
                f" [bright_magenta]{project_pcb_path.stem}[/bright_magenta][bright_cyan].kicad_pcb[/bright_cyan]\n"
                f":point_right: Please re-open [bright_magenta]{project_pcb_path.stem}[/bright_magenta]"
                f" with KiCad, auto-fill reference designators and update the PCB"
                f" from the schematic.",
            )
        )
