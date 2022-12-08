"""
Types for parsing KiCad theme JSON.

SPDX-License-Identifier: EUPL-1.2
"""
from __future__ import annotations

import json
import os

from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    class Config:
        # don't error on extra fields
        # there are some that we haven't accounted for that don't seem to be in kicad_2022
        # e.g. "footprint_text_front"
        extra = "ignore"
        # validate our defaults
        validate_all = True


default: dict
themes_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "json")
default_theme_file = os.path.join(themes_folder, "kicad_2022.json")
with open(default_theme_file) as f:
    default = json.load(f)


class ThreeDViewerTheme(BaseModel):
    background_bottom: str = default["3d_viewer"]["background_bottom"]
    background_top: str = default["3d_viewer"]["background_top"]
    board: str = default["3d_viewer"]["board"]
    copper: str = default["3d_viewer"]["copper"]
    silkscreen_bottom: str = default["3d_viewer"]["silkscreen_bottom"]
    silkscreen_top: str = default["3d_viewer"]["silkscreen_top"]
    soldermask_bottom: str = default["3d_viewer"]["soldermask_bottom"]
    soldermask_top: str = default["3d_viewer"]["soldermask_top"]
    solderpaste: str = default["3d_viewer"]["solderpaste"]
    use_board_stackup_colors: bool = default["3d_viewer"]["use_board_stackup_colors"]


class CopperTheme(BaseModel):
    b: str = default["board"]["copper"]["b"]
    f: str = default["board"]["copper"]["f"]
    in1: str = default["board"]["copper"]["in1"]
    in2: str = default["board"]["copper"]["in2"]
    in3: str = default["board"]["copper"]["in3"]
    in4: str = default["board"]["copper"]["in4"]
    in5: str = default["board"]["copper"]["in5"]
    in6: str = default["board"]["copper"]["in6"]
    in7: str = default["board"]["copper"]["in7"]
    in8: str = default["board"]["copper"]["in8"]
    in9: str = default["board"]["copper"]["in9"]
    in10: str = default["board"]["copper"]["in10"]
    in11: str = default["board"]["copper"]["in11"]
    in12: str = default["board"]["copper"]["in12"]
    in13: str = default["board"]["copper"]["in13"]
    in14: str = default["board"]["copper"]["in14"]
    in15: str = default["board"]["copper"]["in15"]
    in16: str = default["board"]["copper"]["in16"]
    in17: str = default["board"]["copper"]["in17"]
    in18: str = default["board"]["copper"]["in18"]
    in19: str = default["board"]["copper"]["in19"]
    in20: str = default["board"]["copper"]["in20"]
    in21: str = default["board"]["copper"]["in21"]
    in22: str = default["board"]["copper"]["in22"]
    in23: str = default["board"]["copper"]["in23"]
    in24: str = default["board"]["copper"]["in24"]
    in25: str = default["board"]["copper"]["in25"]
    in26: str = default["board"]["copper"]["in26"]
    in27: str = default["board"]["copper"]["in27"]
    in28: str = default["board"]["copper"]["in28"]
    in29: str = default["board"]["copper"]["in29"]
    in30: str = default["board"]["copper"]["in30"]


class BoardTheme(BaseModel):
    anchor: str = default["board"]["anchor"]
    aux_items: str = default["board"]["aux_items"]
    b_adhes: str = default["board"]["b_adhes"]
    b_crtyd: str = default["board"]["b_crtyd"]
    b_fab: str = default["board"]["b_fab"]
    b_mask: str = default["board"]["b_mask"]
    b_paste: str = default["board"]["b_paste"]
    b_silks: str = default["board"]["b_silks"]
    background: str = default["board"]["background"]
    cmts_user: str = default["board"]["cmts_user"]
    copper: CopperTheme = Field(default_factory=CopperTheme)
    cursor: str = default["board"]["cursor"]
    drc_error: str = default["board"]["drc_error"]
    drc_exclusion: str = default["board"]["drc_exclusion"]
    drc_warning: str = default["board"]["drc_warning"]
    dwgs_user: str = default["board"]["dwgs_user"]
    eco1_user: str = default["board"]["eco1_user"]
    eco2_user: str = default["board"]["eco2_user"]
    edge_cuts: str = default["board"]["edge_cuts"]
    f_adhes: str = default["board"]["f_adhes"]
    f_crtyd: str = default["board"]["f_crtyd"]
    f_fab: str = default["board"]["f_fab"]
    f_mask: str = default["board"]["f_mask"]
    f_paste: str = default["board"]["f_paste"]
    f_silks: str = default["board"]["f_silks"]
    footprint_text_invisible: str = default["board"]["footprint_text_invisible"]
    grid: str = default["board"]["grid"]
    grid_axes: str = default["board"]["grid_axes"]
    margin: str = default["board"]["margin"]
    no_connect: str = default["board"]["no_connect"]
    pad_plated_hole: str = default["board"]["pad_plated_hole"]
    pad_through_hole: str = default["board"]["pad_through_hole"]
    plated_hole: str = default["board"]["plated_hole"]
    ratsnest: str = default["board"]["ratsnest"]
    user_1: str = default["board"]["user_1"]
    user_2: str = default["board"]["user_2"]
    user_3: str = default["board"]["user_3"]
    user_4: str = default["board"]["user_4"]
    user_5: str = default["board"]["user_5"]
    user_6: str = default["board"]["user_6"]
    user_7: str = default["board"]["user_7"]
    user_8: str = default["board"]["user_8"]
    user_9: str = default["board"]["user_9"]
    via_blind_buried: str = default["board"]["via_blind_buried"]
    via_hole: str = default["board"]["via_hole"]
    via_micro: str = default["board"]["via_micro"]
    via_through: str = default["board"]["via_through"]
    worksheet: str = default["board"]["worksheet"]


class GerbviewTheme(BaseModel):
    axes: str = default["gerbview"]["axes"]
    background: str = default["gerbview"]["background"]
    dcodes: str = default["gerbview"]["dcodes"]
    grid: str = default["gerbview"]["grid"]
    layers: list[str] = Field(default_factory=lambda: default["gerbview"]["layers"][:])
    negative_objects: str = default["gerbview"]["negative_objects"]
    worksheet: str = default["gerbview"]["worksheet"]


class Meta(BaseModel):
    name: str = default["meta"]["name"]
    version: int = default["meta"]["version"]


class SchematicTheme(BaseModel):
    anchor: str = default["schematic"]["anchor"]
    aux_items: str = default["schematic"]["aux_items"]
    background: str = default["schematic"]["background"]
    brightened: str = default["schematic"]["brightened"]
    bus: str = default["schematic"]["bus"]
    bus_junction: str = default["schematic"]["bus_junction"]
    component_body: str = default["schematic"]["component_body"]
    component_outline: str = default["schematic"]["component_outline"]
    cursor: str = default["schematic"]["cursor"]
    erc_error: str = default["schematic"]["erc_error"]
    erc_warning: str = default["schematic"]["erc_warning"]
    fields: str = default["schematic"]["fields"]
    grid: str = default["schematic"]["grid"]
    grid_axes: str = default["schematic"]["grid_axes"]
    hidden: str = default["schematic"]["hidden"]
    junction: str = default["schematic"]["junction"]
    label_global: str = default["schematic"]["label_global"]
    label_hier: str = default["schematic"]["label_hier"]
    label_local: str = default["schematic"]["label_local"]
    no_connect: str = default["schematic"]["no_connect"]
    note: str = default["schematic"]["note"]
    override_item_colors: bool = default["schematic"]["override_item_colors"]
    pin: str = default["schematic"]["pin"]
    pin_name: str = default["schematic"]["pin_name"]
    pin_number: str = default["schematic"]["pin_number"]
    reference: str = default["schematic"]["reference"]
    shadow: str = default["schematic"]["shadow"]
    sheet: str = default["schematic"]["sheet"]
    sheet_background: str = default["schematic"]["sheet_background"]
    sheet_fields: str = default["schematic"]["sheet_fields"]
    sheet_filename: str = default["schematic"]["sheet_filename"]
    sheet_label: str = default["schematic"]["sheet_label"]
    sheet_name: str = default["schematic"]["sheet_name"]
    value: str = default["schematic"]["value"]
    wire: str = default["schematic"]["wire"]
    worksheet: str = default["schematic"]["worksheet"]


class KicadTheme(BaseModel):
    # we use pydantic.BaseModel instead of dataclasses to be able to alias this field
    _3d_viewer: ThreeDViewerTheme = Field(
        default_factory=ThreeDViewerTheme, alias="3d_viewer"
    )
    board: BoardTheme = Field(default_factory=BoardTheme)
    gerbview: GerbviewTheme = Field(default_factory=GerbviewTheme)
    meta: Meta = Field(default_factory=Meta)
    palette: list[str] = Field(default_factory=list)
    schematic: SchematicTheme = Field(default_factory=SchematicTheme)
