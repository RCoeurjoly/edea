"""
Provides KiCad themes.

SPDX-License-Identifier: EUPL-1.2
"""
from enum import Enum
import json
import os

from edea.draw.themes.types import KicadTheme

__all__ = ["ThemeName", "get_theme"]


class ThemeName(str, Enum):
    EAGLE_DARK = "eagle_dark"
    WLIGHT = "wlight"
    MONOKAI = "monokai"
    WDARK = "wdark"
    BEHAVE_DARK = "behave_dark"
    KICAD_2022 = "kicad_2022"
    NORD = "nord"
    BLUE_TONE = "blue_tone"
    KICAD_CLASSIC = "kicad_classic"
    BLUE_GREEN_DARK = "blue_green_dark"
    KICAD_2020 = "kicad_2020"
    BLACK_WHITE = "black_white"
    SOLARIZED_DARK = "solarized_dark"
    SOLARIZED_LIGHT = "solarized_light"


theme_map: dict[ThemeName, KicadTheme] = {}
themes_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "json")
filenames = {}
for filename in os.listdir(themes_folder):
    if filename.endswith(".json"):
        name, _ = os.path.splitext(filename)

        # throw an error if it's not in our enum
        ThemeName(name)

        filenames[name] = filename


for name in filenames:
    filename = filenames[name]
    with open(os.path.join(themes_folder, filename), encoding="utf8") as f:
        theme_map[name] = KicadTheme(**json.load(f))


def get_theme(name: ThemeName) -> KicadTheme:
    return theme_map[name]