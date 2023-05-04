"""
SPDX-License-Identifier: EUPL-1.2
"""

from packaging.version import parse


def is_kicad_v7(version):
    """Check if the version is 7.0.0 or higher"""
    # remove the suffix
    version = version.split("-")[0]
    return parse(version).major == 7


class KicadVersionError(Exception):
    """Unsupported KiCad version"""
