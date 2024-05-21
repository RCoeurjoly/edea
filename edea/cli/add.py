"""
sub-command for adding edea modules or rules to a project

SPDX-License-Identifier: EUPL-1.2
"""

import os
import pathlib
from tempfile import TemporaryDirectory
from typing import Annotated, Optional

import requests
import rich
import typer
import typer.rich_utils
from click import UsageError
from git import Repo
from pydantic import ValidationError
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn

from edea.kicad.common import VersionError
from edea.kicad.design_rules import DesignRules
from edea.kicad.parser import load_design_rules, load_pcb, load_schematic
from edea.kicad.pcb import Pcb
from edea.kicad.project import KicadProject
from edea.kicad.schematic_group import SchematicGroup
from edea.kicad.serializer import write_pcb

cli = typer.Typer(
    rich_markup_mode="rich",
    help="Add edea modules or rules to your project",
)


def _add_module_from_local_path(module_directory: pathlib.Path):
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


def _add_module_from_git_url(git_url: str, path: pathlib.Path):
    with TemporaryDirectory() as tmp_dir:
        rich.print(f":down_arrow:  Cloning [bright_cyan]{git_url}[/bright_cyan] ...")
        Repo.clone_from(git_url, tmp_dir)
        rich.print(
            f":sparkles: [green]Successfully cloned[/green] [bright_cyan]{git_url}[/bright_cyan] :sparkles:"
        )
        module_directory = pathlib.Path(tmp_dir) / path
        _add_module_from_local_path(module_directory)


def _get_edea_module_or_rule_info(edea_url: str):
    try:
        response = requests.get(edea_url, timeout=5)
    except requests.exceptions.Timeout as e:
        raise UsageError("Request to edea server timed out.") from e
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise UsageError(f"Request to edea server failed: {e}") from e
    return response.json()


def _add_from_edea_url(edea_url: str):
    module_info = _get_edea_module_or_rule_info(edea_url)
    repo_url = module_info["repository"]["url"]
    module_name = module_info["name"]
    _add_module_from_git_url(repo_url, pathlib.Path(module_name))


@cli.command()
def module(
    local_path: Annotated[
        Optional[pathlib.Path],
        typer.Option(
            help="Path to local module directory",
            show_default=False,
        ),
    ] = None,
    git_url: Annotated[
        Optional[str],
        typer.Option(
            help="URL to a git repository containing a module",
            show_default=False,
        ),
    ] = None,
    edea_url: Annotated[
        Optional[str],
        typer.Option(
            help="URL to a module on the edea registry",
            show_default=False,
        ),
    ] = None,
    path: Annotated[
        Optional[pathlib.Path],
        typer.Option(
            help="Path module inside the git directory",
            show_default=False,
        ),
    ] = None,
):
    """

    Add an edea module to your current project.

    .. code-block:: bash

        edea add module --local-dir ../example/
        edea add module --git-url https://gitlab.com/edea-dev/test-modules --path 3v3ldo
        edea add module --edea-url https://edea.com/api/v1/module/79248d65-45a3-4ef3-a7c6-85961d335baa
    """

    if local_path is not None:
        _add_module_from_local_path(local_path)
    elif git_url is not None:
        if path is None:
            raise UsageError(
                "Please provide a path to the module inside the git repository."
            )
        _add_module_from_git_url(git_url, path)
    elif edea_url is not None:
        _add_from_edea_url(edea_url)
    else:
        raise UsageError("Please provide a module directory, git URL, or edea URL.")


def _add_rules_from_local_path(local_path: pathlib.Path):
    if local_path.suffix != ".kicad_dru":
        raise ValueError("The custom design rules have to be in `kicad_dru` format.")
    pro_file = KicadProject.find_pro_file_in_path(pathlib.Path.cwd())
    dest = pathlib.Path.cwd() / pro_file.with_suffix(".kicad_dru").name
    has_design_rules_file = dest.exists()

    if has_design_rules_file:
        project_rules = load_design_rules(dest)
    else:
        project_rules = DesignRules()

    custom_rules = load_design_rules(local_path)
    project_rules.extend(custom_rules)
    project_rules.noramlize()
    dest.write_text(str(project_rules))

    rich.print(
        f":sparkles: [green]Successfully added[/green] [bright_cyan]{local_path}[/bright_cyan] :sparkles:"
    )


def _add_rules_from_git_url(git_url: str, path: pathlib.Path):
    with TemporaryDirectory() as tmp_dir:
        rich.print(f":down_arrow:  Cloning [bright_cyan]{git_url}[/bright_cyan] ...")
        Repo.clone_from(git_url, tmp_dir)
        rich.print(
            f":sparkles: [green]Successfully cloned[/green] [bright_cyan]{git_url}[/bright_cyan] :sparkles:"
        )
        rules_directory = pathlib.Path(tmp_dir) / path
        _add_rules_from_local_path(rules_directory)


def _add_rules_from_edea_url(edea_url: str):
    rules_info = _get_edea_module_or_rule_info(edea_url)
    name = rules_info["name"]
    with TemporaryDirectory() as tmp_dir:
        p = pathlib.Path(tmp_dir) / f"{name}.kicad_dru"
        p.write_text(rules_info["body"])
        _add_rules_from_local_path(p)


@cli.command()
def rules(
    local_path: Annotated[
        Optional[pathlib.Path],
        typer.Option(
            help="Path to local module directory (must be a .kicad_dru file)",
            show_default=False,
        ),
    ] = None,
    git_url: Annotated[
        Optional[str],
        typer.Option(
            help="URL to a git repository containing a module",
            show_default=False,
        ),
    ] = None,
    edea_url: Annotated[
        Optional[str],
        typer.Option(
            help="URL to a module on the edea registry",
            show_default=False,
        ),
    ] = None,
    path: Annotated[
        Optional[pathlib.Path],
        typer.Option(
            help="Path module inside the git directory (must be a .kicad_dru file)",
            show_default=False,
        ),
    ] = None,
):
    """

    Add edea rules to your current project.

    .. code-block:: bash

        edea add rules
    """
    if local_path is not None:
        _add_rules_from_local_path(local_path)
    elif git_url is not None:
        if path is None:
            raise UsageError(
                "Please provide a path to the module inside the git repository."
            )
        _add_rules_from_git_url(git_url, path)
    elif edea_url is not None:
        _add_rules_from_edea_url(edea_url)
