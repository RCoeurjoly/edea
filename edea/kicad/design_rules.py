from dataclasses import field
from textwrap import dedent
from typing import Annotated, Literal, Optional

from pydantic import validator
from pydantic.dataclasses import dataclass
from typing_extensions import Self

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.base import KicadExpr


class Severity(StrEnum):
    error = "error"
    warning = "warning"
    ignore = "ignore"

    def __le__(self, other):
        members = list(Severity.__members__.values())
        return members.index(self) <= members.index(other)

    def __lt__(self, other):
        members = list(Severity.__members__.values())
        return members.index(self) <= members.index(other)


class ConstraintArgType(StrEnum):
    annular_width = "annular_width"
    assertion = "assertion"
    clearance = "clearance"
    connection_width = "connection_width"
    courtyard_clearance = "courtyard_clearance"
    diff_pair_gap = "diff_pair_gap"
    diff_pair_uncoupled = "diff_pair_uncoupled"
    disallow = "disallow"
    edge_clearance = "edge_clearance"
    hole_clearance = "hole_clearance"
    hole_size = "hole_size"
    hole_to_hole = "hole_to_hole"
    length = "length"
    min_resolved_spokes = "min_resolved_spokes"
    physical_clearance = "physical_clearance"
    physical_hole_clearance = "physical_hole_clearance"
    silk_clearance = "silk_clearance"
    text_height = "text_height"
    text_thickness = "text_thickness"
    thermal_relief_gap = "thermal_relief_gap"
    thermal_spoke_width = "thermal_spoke_width"
    track_width = "track_width"
    via_count = "via_count"
    via_diameter = "via_diameter"
    zone_connection = "zone_connection"


@dataclass(config=PydanticConfig, eq=False)
class Rule(KicadExpr):
    name: Annotated[str, m("kicad_always_quotes", "kicad_no_kw")]
    constraint: tuple[ConstraintArgType, tuple[str, ...] | str]
    layer: Optional[str] = None
    severity: Severity = Severity.warning
    condition: Optional[Annotated[str, m("kicad_always_quotes")]] = ""

    def __hash__(self) -> int:
        return hash(
            (self.constraint, self.name, self.layer, self.severity, self.condition)
        )

    @validator("constraint")
    @classmethod
    def _v_constraint(cls, value):
        if isinstance(value[1], tuple):
            # The second half of the consttraint should be treated as a whole
            return (value[0], " ".join(value[1]))
        return value[1]

    def __str__(self) -> str:
        return dedent(
            f"""\
            (rule "{self.name}"
              (layer {self.layer})
              (severity {self.severity})
              (condition "{self.condition}")
              (constraint {self.constraint[0]} ({self.constraint[1]}))
            )"""
        )


@dataclass(config=PydanticConfig, eq=False)
class DesignRules(KicadExpr):
    version: Literal["1"] = "1"
    rules: list[Rule] = field(default_factory=list)

    def noramlize(self):
        """Remove duplicate rules."""
        self.rules = list(dict.fromkeys(self.rules))
        return self

    def extend(self, other: Self):
        if not isinstance(other, DesignRules):
            raise TypeError(f"Cannot extend {self} with {other}")
        self.rules.extend(other.rules)
        return self

    def __str__(self) -> str:
        # TODO: at some point this should be replace by the serializer
        # but the serializer formmating is not good enough yet
        rules = "\n\n".join(str(r) for r in self.rules)
        return f"(version {self.version})\n\n{rules}\n"
