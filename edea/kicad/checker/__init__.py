import datetime
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from httpx import get
from pydantic import BaseModel, root_validator

from edea.kicad.checker.reporter import KicadDrcReporter, KicadErcReporter
from edea.kicad.design_rules import DesignRules, Severity
from edea.kicad.parser import load_design_rules, parse_design_rules
from edea.kicad.project import KicadProject


class CheckResult(BaseModel):
    source: str
    level: Severity
    version: str
    timestamp: datetime.datetime
    dr: Optional[KicadDrcReporter] = None
    er: Optional[KicadErcReporter] = None

    @root_validator
    @classmethod
    def filter_by_level(cls, value: dict) -> dict:
        """Filter and sort violations by severity level."""
        dr: Optional[KicadDrcReporter] = value.get("dr")
        er: Optional[KicadErcReporter] = value.get("er")
        level: Severity = value["level"]

        if isinstance(dr, KicadDrcReporter):
            dr.violations = sorted(
                [v for v in dr.violations if v.severity <= level],
                key=lambda v: v.severity,
            )
            value["dr"] = dr

        if isinstance(er, KicadErcReporter):
            for sheet in er.sheets:
                sheet.violations = sorted(
                    [v for v in sheet.violations if v.severity <= level],
                    key=lambda v: v.severity,
                )
            value["er"] = er
        return value


def check(
    project_dir: Path | str,
    custom_design_rules_path: Path | None = None,
    custom_design_rules_url: str | None = None,
    level: Severity = Severity.ignore,
) -> CheckResult:
    p = Path(project_dir)
    dr, er = None, None

    if p.is_dir():
        kicad_pro_files = list(p.glob("*.kicad_pro"))
        if len(kicad_pro_files) == 0:
            raise FileNotFoundError("Couldn't find project file")
        p = Path(kicad_pro_files[0])

    kicad_sch_path = p.with_suffix(".kicad_sch")
    kicad_pcb_path = p.with_suffix(".kicad_pcb")

    check_both = p.is_dir() or p.suffix == ".kicad_pro"
    if kicad_pcb_path.exists() and (check_both or p.suffix == ".kicad_pcb"):
        with custom_design_rules(
            custom_design_rules_path, custom_design_rules_url, kicad_pcb_path.parent
        ):
            dr = KicadDrcReporter.from_kicad_file(kicad_pcb_path)

    if kicad_sch_path.exists() and (check_both or p.suffix == ".kicad_sch"):
        er = KicadErcReporter.from_kicad_file(kicad_sch_path)

    if (selected_reporter := dr or er) is None:
        raise FileNotFoundError("Couldn't find `.kicad_pcb` or `.kicad_sch` file")

    return CheckResult(
        source=selected_reporter.source,
        version=selected_reporter.kicad_version,
        timestamp=selected_reporter.date,
        dr=dr,
        er=er,
        level=level,
    )


def find_design_rules_file(project_path: Path):
    pro_file = KicadProject.find_pro_file_in_path(project_path)
    dest = project_path / pro_file.with_suffix(".kicad_dru").name
    has_design_rules_file = dest.exists()

    if has_design_rules_file:
        project_rules = load_design_rules(dest)
    else:
        project_rules = DesignRules()

    return dest, project_rules


@contextmanager
def custom_design_rules(
    custom_rules_path: Path | None,
    custom_design_rules_url: str | None,
    project_path: Path,
):
    """Add the design rules to project and delete it on exiting the context."""
    if custom_rules_path is None and custom_design_rules_url is None:
        yield
        return
    dest, project_rules = find_design_rules_file(project_path)
    has_design_rules_file = dest.exists()
    if has_design_rules_file:
        original_text = dest.read_text()
    else:
        original_text = ""  # just to make pylance happy

    try:
        # loading rules could fail.
        if custom_rules_path is not None:
            custom_rules = load_design_rules(custom_rules_path)
            project_rules.extend(custom_rules)
        if custom_design_rules_url is not None:
            remote_dr = _get_remote_dr_file_content(custom_design_rules_url)
            remote_rules = parse_design_rules(remote_dr)
            project_rules.extend(remote_rules)
        project_rules.noramlize()
        dest.write_text(str(project_rules))
        yield dest
    except Exception as e:
        raise ValueError(f"Couldn't load design rules: {e}") from e
    finally:
        # this operation should be idempotent
        if has_design_rules_file:
            dest.write_text(original_text)
        else:
            dest.unlink()


def _get_remote_dr_file_content(rule_set_url: str):
    response = get(rule_set_url)
    response.raise_for_status()

    json: dict[str, str] = response.json()
    return json["body"]
