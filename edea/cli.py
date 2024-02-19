"""
edea command line tool

SPDX-License-Identifier: EUPL-1.2
"""

import os
import pathlib
import re
from collections import Counter
from typing import Annotated, Optional

import rich
import typer
import typer.rich_utils
from click import UsageError
from pydantic import ValidationError
from rich.markup import escape
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn

from edea.kicad import checker
from edea.kicad.checker.drc import CoordinateUnits, Severity, Violation
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
    ...


@cli.command()
def add(
    module_directory: pathlib.Path,
):
    """

    Add an edea module to your current project.

    .. code-block:: bash

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


def _format_violation(
    vs: list[Violation],
    unit: CoordinateUnits | None,
    title: str,
    ignore_regex: re.Pattern[str],
):
    violations_counter = Counter(v.severity for v in vs)
    num_err, num_warn, num_ignore = (
        violations_counter[Severity.error],
        violations_counter[Severity.warning],
        violations_counter[Severity.ignore],
    )
    body = (
        f"\n{num_err} errors" + f", {num_warn} warnings \n"
        if num_warn > 0
        else "\n" + f"{num_ignore} ignored \n"
        if num_ignore > 0
        else ""
    )
    for v in vs:
        if v.severity == Severity.error:
            symbol = ":x:"
            short = f"[red](error:{v.type})[/red]"
        elif v.severity == Severity.warning:
            symbol = ":warning: "
            short = f"[bright_yellow](warning:{v.type})[/bright_yellow]"
        else:
            symbol = ":person_shrugging:"
            short = f"[grey46](ignored:{v.type})[/grey46]"

        u = "" if unit is None else unit.value
        items = "\n".join(
            [
                f"[bright_magenta]{escape(i.description)}[/bright_magenta] ({i.uuid})"
                f"\n   @ [bright_magenta]({i.pos.x} {u}, {i.pos.y} {u})[/bright_magenta]"
                for i in v.items
            ]
        )

        message = f"\n\n{symbol} {escape(v.description)} {short}\n   {items}"
        if re.search(ignore_regex, message) is None:
            # if the message doesn't include the ignored regex pattern add it to the violations string
            body += message
    if len(body) == 0:
        return None
    return Panel.fit(body, title=title)


@cli.command()
def check(
    project_or_file: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to project directory, kicad_pro, kicad_sch, or kicad_pcb files",
            show_default=False,
        ),
    ],
    custom_dr: Annotated[
        Optional[pathlib.Path],
        typer.Option(help="Path to custom design rules (.kicad_dru)"),
    ] = None,
    drc: Annotated[bool, typer.Option(help="Check design rules")] = True,
    erc: Annotated[bool, typer.Option(help="Check electrical rules")] = True,
    ignore_regex: Annotated[
        str, typer.Option(help="Ignore violations that include the specified regex")
    ] = r"a^",
    level: Severity = Severity.warning,
):
    """
    Check design and electrical rules for kicad project.

    .. code-block:: bash

        edea check example                    # checks design and electrical rules
        edea check example --no-drc           # checks design rules
        edea check example --no-erc           # checks electrical rules
        edea check example/example.kicad_pro  # checks design and electrical rules
        edea check example/example.kicad_sch  # checks electrical rules
        edea check example/example.kicad_pcb  # checks design rules
    """
    try:
        result = checker.check(project_or_file, custom_dr, level)
    except (FileNotFoundError, ValueError) as e:
        raise UsageError(str(e)) from e

    rich.print(
        f"Design rules checked for [bright_cyan]{result.source}[/bright_cyan] \n"
        f"using Kicad [bright_magenta]{result.version}[/bright_magenta]"
        f" at [bright_magenta]{result.timestamp}[/bright_magenta]."
    )

    compiled_ignore_regex = re.compile(ignore_regex)

    dr = result.dr
    if dr is not None:
        dr_msg = _format_violation(
            dr.violations,
            dr.coordinate_units,
            ":art:" * 3 + " Found the following design violations " + ":art:" * 3,
            compiled_ignore_regex,
        )
        if drc and dr_msg is not None:
            rich.print(dr_msg)

    er = result.er
    if er is not None:
        er_msg = _format_violation(
            er.violations,
            er.coordinate_units,
            ":zap:" * 3 + " Found the following electrical violations " + ":zap:" * 3,
            compiled_ignore_regex,
        )
        if erc and er_msg is not None:
            rich.print(er_msg)
