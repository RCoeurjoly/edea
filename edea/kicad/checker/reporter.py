"""Load KiCad reports and generate reports from KiCAD files.
"""

import json
import pathlib
import tempfile
from abc import abstractmethod

from edea.kicad._kicad_cli import kicad_cli
from edea.kicad.checker.drc import KicadDRCReport
from edea.kicad.checker.erc import KicadERCReport


class RCReporter:
    """
    KiCad checker report generator.
    """

    @classmethod
    def from_json_report(cls, path: str | pathlib.Path):
        """
        Creates a reporter instance from a JSON report file.

        :param path: The path to the JSON report file.

        :returns: Instance of RCReporter.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    @staticmethod
    @abstractmethod
    def _kicad_cli_command() -> list[str | pathlib.Path]:
        """
        Build the arguments to interact with the KiCad command line interface.

        :returns: List of command-line arguments for the KiCad command line interface.
        """
        raise NotImplementedError

    @classmethod
    def from_kicad_file(cls, path: str | pathlib.Path):
        """
        Creates a reporter instance from a KiCad file.

        :param path: The path to the KiCad file.

        :returns: Instance of RCReporter.
        """
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


class KicadERCReporter(RCReporter, KicadERCReport):
    """
    A KiCad Electrical Rule Check (ERC).
    """

    @staticmethod
    def _kicad_cli_command():
        return ["sch", "erc"]


class KicadDRCReporter(KicadDRCReport, RCReporter):
    """
    A KiCad Design Rule Check (DRC).
    """

    @staticmethod
    def _kicad_cli_command():
        return ["pcb", "drc"]
