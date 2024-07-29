"""
Partially generated by datamodel-codegen:
   filename:  https://gitlab.com/kicad/code/kicad/-/raw/master/resources/schemas/drc.v1.json
   timestamp: 2024-01-03T16:11:36+00:00
"""

# pylint: disable=duplicate-code

from __future__ import annotations

from datetime import datetime
from typing import Annotated, List
from uuid import UUID

from pydantic import BaseModel, Extra, Field, constr

from edea.kicad._str_enum import StrEnum
from edea.kicad.design_rules import Severity


class CoordinateUnits(StrEnum):
    mm = "mm"
    mils = "mils"
    in_ = "in"


class Coordinate(BaseModel):
    class Config:
        """
        :meta private:
        """

        extra = Extra.forbid

    x: float = Field(..., description="x coordinate")
    y: float = Field(..., description="y coordinate")


class AffectedItem(BaseModel):
    class Config:
        """
        :meta private:
        """

        extra = Extra.forbid

    uuid: UUID
    description: str = Field(..., description="Description of the item")
    pos: Coordinate


class Violation(BaseModel):
    class Config:
        """
        :meta private:
        """

        extra = Extra.forbid

    type: str = Field(..., description="KiCad type name for the violation")
    description: str = Field(..., description="Description of the violation")
    severity: Severity
    items: List[AffectedItem]


class KicadDRCReport(BaseModel):
    class Config:
        """
        :meta private:
        """

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
    violations: List[Violation]
    unconnected_items: List[Violation]
    schematic_parity: List[Violation]
    coordinate_units: CoordinateUnits = Field(
        ..., description="Units that all coordinates in this report are encoded in"
    )
