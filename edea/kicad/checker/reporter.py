import json
import pathlib
import tempfile
from abc import abstractmethod

from edea.kicad._kicad_cli import kicad_cli
from edea.kicad.checker.drc import KicadDrcReport
from edea.kicad.checker.erc import KicadErcReport


class RCReporter:
    @classmethod
    def from_json_report(cls, path: str | pathlib.Path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    @staticmethod
    @abstractmethod
    def _kicad_cli_command() -> list[str | pathlib.Path]:
        ...

    @classmethod
    def from_kicad_file(cls, path: str | pathlib.Path):
        with tempfile.NamedTemporaryFile() as f:
            kicad_cli(
                cls._kicad_cli_command()
                + [
                    str(path),
                    "--format",
                    "json",
                    "-o",
                    f.name,
                ]
            )
            return cls.from_json_report(f.name)


class KicadErcReporter(RCReporter, KicadErcReport):
    @staticmethod
    def _kicad_cli_command():
        return ["sch", "erc"]


class KicadDrcReporter(KicadDrcReport, RCReporter):
    @staticmethod
    def _kicad_cli_command():
        return ["pcb", "drc"]
