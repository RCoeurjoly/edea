from __future__ import annotations

import pathlib
from typing import Any, NamedTuple, Optional
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Extra, Field


class BaseModel(PydanticBaseModel):
    class Config:
        # we haven't defined all the fields yet so we allow extra ones
        extra = Extra.allow
        # validate our defaults
        validate_all = True


class Dimensions(BaseModel):
    arrow_length: int
    extension_offset: int
    keep_text_aligned: bool
    suppress_zeroes: bool
    text_position: int
    units_format: int


class Pads(BaseModel):
    drill: float
    height: float
    width: float


class Zones(BaseModel):
    field_45_degree_only: Optional[bool] = Field(default=None, alias="45_degree_only")
    min_clearance: float


class Defaults(BaseModel):
    board_outline_line_width: Optional[float]
    copper_line_width: Optional[float]
    copper_text_italic: Optional[bool]
    copper_text_size_h: Optional[float]
    copper_text_size_v: Optional[float]
    copper_text_thickness: Optional[float]
    copper_text_upright: Optional[bool]
    courtyard_line_width: Optional[float]
    dimension_precision: Optional[int]
    dimension_units: Optional[int]
    dimensions: Optional[Dimensions]
    fab_line_width: Optional[float]
    fab_text_italic: Optional[bool]
    fab_text_size_h: Optional[float]
    fab_text_size_v: Optional[float]
    fab_text_thickness: Optional[float]
    fab_text_upright: Optional[bool]
    other_line_width: Optional[float]
    other_text_italic: Optional[bool]
    other_text_size_h: Optional[float]
    other_text_size_v: Optional[float]
    other_text_thickness: Optional[float]
    other_text_upright: Optional[bool]
    pads: Optional[Pads]
    silk_line_width: Optional[float]
    silk_text_italic: Optional[bool]
    silk_text_size_h: Optional[float]
    silk_text_size_v: Optional[float]
    silk_text_thickness: Optional[float]
    silk_text_upright: Optional[bool]
    zones: Optional[Zones]


class Meta(BaseModel):
    filename: Optional[str]
    version: int


class Rules(BaseModel):
    allow_blind_buried_vias: Optional[bool]
    allow_microvias: Optional[bool]
    max_error: Optional[float]
    min_clearance: Optional[float]
    min_connection: Optional[float]
    min_copper_edge_clearance: Optional[float]
    solder_mask_clearance: Optional[float]
    solder_mask_min_width: Optional[float]
    solder_paste_clearance: Optional[float]
    solder_paste_margin_ratio: Optional[float]
    min_hole_clearance: Optional[float]
    min_hole_to_hole: Optional[float]
    min_microvia_diameter: Optional[float]
    min_microvia_drill: Optional[float]
    min_resolved_spokes: Optional[int]
    min_silk_clearance: Optional[float]
    min_text_height: Optional[float]
    min_text_thickness: Optional[float]
    min_through_hole_diameter: Optional[float]
    min_track_width: Optional[float]
    min_via_annular_width: Optional[float]
    min_via_diameter: Optional[float]
    solder_mask_to_copper_clearance: Optional[float]
    use_height_for_length_calcs: Optional[bool]


class TeardropOption(BaseModel):
    td_allow_use_two_tracks: Optional[bool]
    td_curve_segcount: Optional[int]
    td_on_pad_in_zone: Optional[bool]
    td_onpadsmd: Optional[bool]
    td_onroundshapesonly: Optional[bool]
    td_ontrackend: Optional[bool]
    td_onviapad: Optional[bool]


class TeardropParameter(BaseModel):
    td_curve_segcount: int
    td_height_ratio: float
    td_length_ratio: float
    td_maxheight: float
    td_maxlen: float
    td_target_name: str
    td_width_to_size_filter_ratio: Optional[float]


class ViaDimension(BaseModel):
    diameter: float
    drill: float


class DesignSettings(BaseModel):
    apply_defaults_to_field: Optional[bool]
    apply_defaults_to_shapes: Optional[bool]
    apply_defaults_to_fp_text: Optional[bool]
    defaults: Defaults
    diff_pair_dimensions: list
    drc_exclusions: list
    meta: Optional[Meta]
    rule_severities: Optional[dict[str, Any]]
    rule_severitieslegacy_courtyards_overlap: Optional[bool]
    rule_severitieslegacy_no_courtyard_defined: Optional[bool]
    rules: Rules
    teardrop_options: Optional[list[TeardropOption]]
    teardrop_parameters: Optional[list[TeardropParameter]]
    track_widths: list[float]
    via_dimensions: list[ViaDimension]
    zones_allow_external_fillets: Optional[bool]
    zones_use_no_outline: Optional[bool]


class Board(BaseModel):
    field_3dviewports: Optional[list] = Field(default=None, alias="3dviewports")
    design_settings: DesignSettings
    layer_presets: list
    viewports: Optional[list]


class Cvpcb(BaseModel):
    equivalence_files: list


class Erc(BaseModel):
    erc_exclusions: list
    meta: Meta
    pin_map: list[list[int]]
    rule_severities: dict[str, Any]


class Libraries(BaseModel):
    pinned_footprint_libs: list
    pinned_symbol_libs: list


class Class(BaseModel):
    bus_width: int
    clearance: float
    diff_pair_gap: float
    diff_pair_via_gap: float
    diff_pair_width: float
    line_style: int
    microvia_diameter: float
    microvia_drill: float
    name: str
    pcb_color: str
    schematic_color: str
    track_width: float
    via_diameter: float
    via_drill: float
    wire_width: int


class NetclassPattern(BaseModel):
    netclass: str
    pattern: str


class NetSettings(BaseModel):
    classes: list[Class]
    meta: Meta
    net_colors: Optional[dict[str, str]]
    netclass_assignments: Optional[dict[str, str]]
    netclass_patterns: Optional[list[NetclassPattern]]


class LastPaths(BaseModel):
    gencad: str
    idf: str
    netlist: str
    specctra_dsn: str
    step: str
    vrml: str


class Pcbnew(BaseModel):
    last_paths: LastPaths
    page_layout_descr_file: str


class Drawing(BaseModel):
    dashed_lines_dash_length_ratio: Optional[float]
    dashed_lines_gap_length_ratio: Optional[float]
    default_line_thickness: Optional[float]
    default_text_size: Optional[float]
    default_bus_thickness: Optional[float]
    default_junction_size: Optional[float]
    default_wire_thickness: Optional[float]
    field_names: Optional[list]
    intersheets_ref_own_page: Optional[bool]
    intersheets_ref_prefix: Optional[str]
    intersheets_ref_short: Optional[bool]
    intersheets_ref_show: Optional[bool]
    intersheets_ref_suffix: Optional[str]
    junction_size_choice: Optional[int]
    label_size_ratio: Optional[float]
    pin_symbol_size: Optional[float]
    text_offset_ratio: Optional[float]


class Ngspice(BaseModel):
    fix_include_paths: Optional[bool]
    fix_passive_vals: Optional[bool]
    meta: Optional[Meta]
    model_mode: Optional[int]
    workbook_filename: Optional[str]


class ProjectSchematic(BaseModel):
    annotate_start_num: Optional[int]
    drawing: Optional[Drawing]
    legacy_lib_dir: str
    legacy_lib_list: list
    meta: Optional[Meta]
    net_format_name: Optional[str]
    ngspice: Optional[Ngspice]
    page_layout_descr_file: Optional[str]
    plot_directory: Optional[str]
    spice_adjust_passive_values: Optional[bool]
    spice_current_sheet_as_root: Optional[bool]
    spice_external_command: Optional[str]
    spice_model_current_sheet_as_root: Optional[bool]
    spice_save_all_currents: Optional[bool]
    spice_save_all_voltages: Optional[bool]
    subpart_first_id: Optional[int]
    subpart_id_separator: Optional[int]


class ProjectSheet(NamedTuple):
    uuid: UUID
    name: str


class KicadProject(BaseModel):
    board: Board
    boards: list
    cvpcb: Cvpcb
    erc: Optional[Erc]
    libraries: Libraries
    meta: Meta
    net_settings: NetSettings
    pcbnew: Pcbnew
    schematic: ProjectSchematic
    sheets: list[ProjectSheet]
    text_variables: dict[str, Any]

    @staticmethod
    def find_pro_file_in_path(project_path: pathlib.Path):
        pro_files = list(project_path.glob("*.kicad_pro"))
        if len(pro_files) == 0:
            raise FileNotFoundError("Couldn't find project file")
        else:
            pro_file = pro_files[0]
        return pro_file
