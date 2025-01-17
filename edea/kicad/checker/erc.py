"""
Partially generated by datamodel-codegen:
   filename:  https://gitlab.com/kicad/code/kicad/-/raw/master/resources/schemas/erc.v1.json
   timestamp: 2024-01-04T10:32:53+00:00
"""

# pylint: disable=duplicate-code

from __future__ import annotations

from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Extra, Field, constr

from edea.kicad.checker.drc import CoordinateUnits, Violation


class Sheet(BaseModel):
    class Config:
        extra = Extra.forbid

    uuid_path: str
    path: str = Field(..., description="KiCad type name for the violation")
    violations: List[Violation]


class KicadErcReport(BaseModel):
    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True

    field_schema: str | None = Field(
        alias="$schema", description="JSON schema reference"
    )
    source: str = Field(..., description="Source file path")
    date: datetime = Field(..., description="Time at generation of report")
    kicad_version: Annotated[
        str, constr(regex=r"^\d{1,2}(\.\d{1,2}(\.\d{1,2})?)?$")
    ] = Field(..., description="KiCad version used to generate the report")
    sheets: List[Sheet]
    coordinate_units: Optional[CoordinateUnits] = Field(
        None, description="Units that all coordinates in this report are encoded in"
    )

    @property
    def violations(self) -> List[Violation]:
        return [v for sheet in self.sheets for v in sheet.violations]
