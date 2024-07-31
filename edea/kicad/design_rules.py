"""Represents kicad design rules.
"""

from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.base import KicadExpr


class Severity(StrEnum):
    """
    Different severity levels for checker violations.
    """

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
    """
    Different types of arguments used in PCB design constraints.
    """

    annular_width = "annular_width"
    """
    Width of the annular ring in a plated through-hole.
    """
    assertion = "assertion"
    """
    Custom assertion statement within a constraint.
    """
    clearance = "clearance"
    """
    Minimum distance between two objects on the PCB layout.
    """
    connection_width = "connection_width"
    """
    Width of a connection element in the design.
    """
    courtyard_clearance = "courtyard_clearance"
    """
    Minimum distance between an object and its courtyard.
    """
    diff_pair_gap = "diff_pair_gap"
    """
    Spacing between two traces in a differential pair.
    """
    diff_pair_uncoupled = "diff_pair_uncoupled"
    """
    Diff pair is not routed together.
    """
    disallow = "disallow"
    """
    Constraint that disallows a specific action or configuration.
    """
    edge_clearance = "edge_clearance"
    """
    Minimum distance between an object and the PCB edge.
    """
    hole_clearance = "hole_clearance"
    """
    Minimum distance between an object and a hole.
    """
    hole_size = "hole_size"
    """
    Diameter of a drilled hole.
    """
    hole_to_hole = "hole_to_hole"
    """
    Distance between two drilled holes.
    """
    length = "length"
    """
    Length of a trace or other geometric element.
    """
    min_resolved_spokes = "min_resolved_spokes"
    """
    Minimum number of connected spokes in a thermal relief pattern.
    """
    physical_clearance = "physical_clearance"
    """
    Physical clearance between objects in the manufactured PCB.
    """
    physical_hole_clearance = "physical_hole_clearance"
    """
    Physical clearance between an object and a drilled hole in the manufactured PCB.
    """
    silk_clearance = "silk_clearance"
    """
    Minimum distance between an object and the silkscreen layer.
    """
    text_height = "text_height"
    """
    Height of text elements on the PCB.
    """
    text_thickness = "text_thickness"
    """
    Thickness of text stroke on the PCB.
    """
    thermal_relief_gap = "thermal_relief_gap"
    """
    Gap between a trace and the edge of a thermal relief pattern.
    """
    thermal_spoke_width = "thermal_spoke_width"
    """
    Width of spokes in a thermal relief pattern.
    """
    track_width = "track_width"
    """
    Width of a conductive trace on the PCB.
    """
    via_count = "via_count"
    """
    Number of vias used in a connection.
    """
    via_diameter = "via_diameter"
    """
    Diameter of a via (plated through-hole).
    """
    zone_connection = "zone_connection"
    """
    Connection between a zone and another object on the PCB.
    """


@dataclass(config=PydanticConfig, eq=False)
class Rule(KicadExpr):
    """
    A design rule for a KiCad PCB layout.

    :param name: The name of the rule.
    :param constraint: The design rule constraint.
    :param layer: The PCB layer where the rule applies.
    :param severity: The severity level of the rule violation.
    :param condition: An optional KiCad expression representing a condition under which the rule applies.
    """

    name: Annotated[str, m("kicad_always_quotes", "kicad_no_kw")]
    constraint: (
        tuple[ConstraintArgType, tuple[str, ...] | str]
        | tuple[ConstraintArgType, tuple[str, ...] | str, tuple[str, ...] | str]
    )
    layer: Optional[str] = None
    severity: Optional[Severity] = None
    condition: Optional[Annotated[str, m("kicad_always_quotes")]] = ""
    kicad_expr_tag_name: ClassVar[Literal["rule"]] = "rule"

    def __hash__(self) -> int:
        return hash(
            (self.constraint, self.name, self.layer, self.severity, self.condition)
        )

    @validator("constraint")
    @classmethod
    def _v_constraint(cls, value):
        if isinstance(value[1], tuple):
            if len(value) == 3:
                # The second half of the consttraint should be treated as a whole
                return (value[0], " ".join(value[1]), " ".join(value[2]))
            # The second half of the consttraint should be treated as a whole
            return (value[0], " ".join(value[1]))

        return value[1]

    def __str__(self) -> str:
        """Not the nicest code but it makes the output look like the original file."""
        constrain_expr = f"({self.constraint[1]})" + (
            f" ({self.constraint[2]})" if len(self.constraint) == 3 else ""
        )
        lines = [
            f'(rule "{self.name}"',
            f'  {"(layer " + str(self.layer) + ")" if self.layer is not None else ""}',
            f'  {"(severity " + str(self.severity) + ")" if self.severity else ""}',
            f"""  {'(condition "' + str(self.condition) + '")' if self.condition else ""}""",
            f"  (constraint {self.constraint[0]} {constrain_expr})",
            ")",
        ]
        return "\n".join(line for line in lines if line.strip()).strip()


@dataclass(config=PydanticConfig, eq=False)
class DesignRuleSet(KicadExpr):
    """
    A collection of design rules for a KiCad PCB layout.

    :param version: supported version of kicad_dru file.
    :param rules: A list of `Rule` objects defining the individual design rules for the PCB layout.
    """

    version: Literal["1"] = "1"
    rules: list[Rule] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["design_rules"]] = "design_rules"

    def noramlize(self):
        """
        Remove duplicate rules.

        :returns: The 'DesignRules' object itself after removing duplicates.
        """
        self.rules = list(dict.fromkeys(self.rules))
        return self

    def extend(self, other: "DesignRuleSet"):
        """
        Merge another set of design rules into the current one.

        :param other: Another set of design rules.

        :returns: The extended design rules object.
        :raises TypeError: : If the provided argument is not a 'DesignRules' instance.
        """
        if not isinstance(other, DesignRuleSet):
            raise TypeError(f"Cannot extend {self} with {other}")
        self.rules.extend(other.rules)
        return self

    def __str__(self) -> str:
        """
        Returns a string representation of the design rules in KiCad format.

        :returns: The string representation of the design rules in KiCad format.
        """
        # TODO: at some point this should be replace by the serializer
        # but the serializer formmating is not good enough yet
        rules = "\n\n".join(str(r) for r in self.rules)
        return f"(version {self.version})\n\n{rules}\n"
