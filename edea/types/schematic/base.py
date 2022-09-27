"""
Provides our KicadSchExpr class which we use as a base for all our schematic
related KiCad s-expressions.

SPDX-License-Identifier: EUPL-1.2
"""
from pydantic import validator

from edea.types.base import KicadExpr


class KicadSchExpr(KicadExpr):
    @validator("at", pre=True, check_fields=False)
    def validate_at_rotation(cls, value):
        """
        In schematic files only four rotations are exposed in the KiCad GUI. We
        use a `Literal` type for these so need to convert to `int` manually.
        We've also seen unecessary rotations such as 900° in the wild hence `% 360`.
        """
        if len(value) == 3:
            return (value[0], value[1], int(value[2]) % 360)
        return value
