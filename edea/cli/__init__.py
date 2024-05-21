"""
edea command line tool

SPDX-License-Identifier: EUPL-1.2
"""

import importlib.metadata
import pathlib
import re
from collections import Counter
from typing import Annotated, Optional

import rich
import typer
import typer.rich_utils
from click import UsageError
from rich.markup import escape
from rich.panel import Panel

from edea.cli import add
from edea.kicad import checker
from edea.kicad.checker.drc import CoordinateUnits, Severity, Violation

# https://github.com/tiangolo/typer/issues/437
typer.rich_utils.STYLE_HELPTEXT = ""

cli = typer.Typer(
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

cli.add_typer(add.cli, name="add")


@cli.callback()
def cli_root():
    ...


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
    custom_dr_url: Annotated[
        Optional[str],
        typer.Option(
            help="URL to custom design rules hosted on edea portal server.",
        ),
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
        result = checker.check(project_or_file, custom_dr, custom_dr_url, level)
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


@cli.command()
def version():
    """
    Print the version of edea.

    .. code-block:: bash
        edea version
    """

    v = importlib.metadata.version("edea")

    rich.print(f"edea version: [bright_magenta]{v}[/bright_magenta]")
