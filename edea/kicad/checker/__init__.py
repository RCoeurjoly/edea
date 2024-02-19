import datetime
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, root_validator

from edea.kicad.checker.reporter import KicadDrcReporter, KicadErcReporter
from edea.kicad.design_rules import Severity
from edea.kicad.parser import load_design_rules


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
        with custom_design_rules(custom_design_rules_path, kicad_pcb_path.parent):
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


@contextmanager
def custom_design_rules(custom_rules_path: Path | None, project_path: Path):
    """Copy the design rules to project directory and delete it on exiting the context."""
    if custom_rules_path is None:
        yield
        return

    if custom_rules_path.suffix != ".kicad_dru":
        raise ValueError("The custom design rules have to be in `kicad_dru` format.")

    pcb_file = list(project_path.glob("*.kicad_pro"))
    if len(pcb_file) == 0:
        raise FileNotFoundError("Couldn't find project file")
    else:
        pcb_file = pcb_file[0]

    dest = project_path / pcb_file.with_suffix(".kicad_dru").name

    if dest.exists():
        original_text = dest.read_text()
        try:
            project_rules = load_design_rules(dest)
            custom_rules = load_design_rules(custom_rules_path)
            project_rules.extend(custom_rules)
            project_rules.noramlize()
            dest.write_text(str(project_rules))
            yield dest
        finally:
            # this operation should be idempotent
            dest.write_text(original_text)
    else:
        # otherwise, copy the custom rules to the project directory
        try:
            shutil.copy(custom_rules_path, dest)
            yield dest
        finally:
            if dest.exists():
                dest.unlink()