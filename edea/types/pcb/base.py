"""
Provides our KicadPcbExpr class which we use as a base for all our PCB
related KiCad s-expressions.

SPDX-License-Identifier: EUPL-1.2
"""

from pydantic import validator

from edea.types.base import KicadExpr


class KicadPcbExpr(KicadExpr):
    @validator("locked", pre=True, check_fields=False)
    def _locked(cls, v):
        """Handle the type conversion of the `locked` field."""
        if v is None:
            return None
        if v == "locked":
            return True
        if isinstance(v, bool):
            return v

        raise ValueError(f"Unknown value for locked: {v} in {cls}")
