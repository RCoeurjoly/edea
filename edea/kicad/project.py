"""Dataclasses describing the contents of .kicad_pro files.
"""

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
    """
    The dimensions configuration.

    :param arrow_length: The length of the arrow.
    :param extension_offset: The offset for extension.
    :param keep_text_aligned: A flag to keep text aligned.
    :param suppress_zeroes: A flag to suppress zeroes.
    :param text_position: The position of the text.
    :param units_format: The format of the units.
    """

    arrow_length: int
    extension_offset: int
    keep_text_aligned: bool
    suppress_zeroes: bool
    text_position: int
    units_format: int


class Pads(BaseModel):
    """
    The pad configuration.

    :param drill: The drill size.
    :param height: The height of the pad.
    :param width: The width of the pad.
    """

    drill: float
    height: float
    width: float


class Zones(BaseModel):
    """
    The zone configuration.

    :param field_45_degree_only: A flag for 45-degree clearance.
    :param min_clearance: The minimum clearance.
    """

    field_45_degree_only: Optional[bool] = Field(default=None, alias="45_degree_only")
    min_clearance: float


class Defaults(BaseModel):
    """
    Various configuration options related to the visual appearance of a PCB layout.

    :param board_outline_line_width: The board outline line width.
    :param copper_line_width: The copper traces line width.
    :param copper_text_italic: Whether copper text should be italic or not.
    :param copper_text_size_h: The horizontal size of copper text.
    :param copper_text_size_v: The vertical size of copper text.
    :param copper_text_thickness: The thickness of copper text.
    :param copper_text_upright: Whether copper text should be upright or not.
    :param courtyard_line_width: The width of the line used to draw component courtyards.
    :param dimension_precision: The precision (number of decimal places) used for dimensions.
    :param dimension_units: The mesurement units (e.g., millimeters, inches) used for dimensions.
    :param dimensions: Instance of the :py:class:`Dimensions`  representing dimensions configuration.
    :param fab_line_width: The width of the line used to draw fabrication lines.
    :param fab_text_italic: Whether fabrication text should be italicized or not.
    :param fab_text_size_h: The horizontal size of fabrication text.
    :param fab_text_size_v: The vertical size of fabrication text.
    :param fab_text_thickness: The thickness of fabrication text.
    :param fab_text_upright: Whether fabrication text should be upright or not.
    :param other_line_width: The width of the line used for miscellaneous features.
    :param other_text_italic: Whether miscellaneous text should be italicized or not.
    :param other_text_size_h: The horizontal size of miscellaneous text.
    :param other_text_size_v: The vertical size of miscellaneous text.
    :param other_text_thickness: The thickness of miscellaneous text.
    :param other_text_upright: Whether miscellaneous text should be upright or not.
    :param pads: Instance of the :py:class:`Pads`, representing pad configuration.
    :param silk_line_width: The width of the line used for silkscreen features.
    :param silk_text_italic: Whether the silkscreen text should be italicized or not.
    :param silk_text_size_h: The horizontal size of silkscreen text.
    :param silk_text_size_v: The vertical size of silkscreen text.
    :param silk_text_thickness: The thickness of silkscreen text.
    :param silk_text_upright: Whether the silkscreen text should be upright or not.
    :param zones: Instance of :py:class:`Zones`, representing zone configuration.
    """

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
    """
    Stores metadata associated with project files.

    :param filename: The file name.
    :param version: The version kicad format.
    """

    filename: Optional[str]
    version: int


class Rules(BaseModel):
    """
    Various design rules used for validating a PCB layout.

    :param allow_blind_buried_vias: Whether blind and buried vias are allowed or not.
    :param allow_microvias: Whether microvias are allowed or not.
    :param max_error: The maximum allowed error during design rule checks.
    :param min_clearance: The minimum clearance between objects on the PCB.
    :param min_connection: The minimum allowed size for connections (e.g., traces).
    :param min_copper_edge_clearance: The minimum clearance between copper features and other objects.
    :param solder_mask_clearance: The clearance between solder mask and other objects.
    :param solder_mask_min_width: The minimum width of solder mask features.
    :param solder_paste_clearance: The clearance between solder paste and other objects.
    :param solder_paste_margin_ratio: The ratio defining the margin for solder paste application.
    :param min_hole_clearance: The minimum clearance between holes.
    :param min_hole_to_hole: The minimum distance between center points of holes.
    :param min_microvia_diameter: The minimum diameter for microvias.
    :param min_microvia_drill: The minimum drill size for microvias.
    :param min_resolved_spokes: The minimum number of spokes allowed in rounded corners.
    :param min_silk_clearance: The minimum clearance between silkscreen features and other objects.
    :param min_text_height: The minimum height of text on the PCB.
    :param min_text_thickness: The minimum thickness of text on the PCB.
    :param min_through_hole_diameter: The minimum diameter for through-hole pads.
    :param min_track_width: The minimum allowed width for tracks (traces).
    :param min_via_annular_width: The minimum width of the annular ring around vias.
    :param min_via_diameter: The minimum diameter for vias.
    :param solder_mask_to_copper_clearance: The clearance between solder mask and copper features.
    :param use_height_for_length_calcs: Whether to use via height for length calculations or not.
    """

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
    """
    The options controlling the generation of teardrops on the PCB layout.

    :param td_allow_use_two_tracks: Whether two tracks can be used to form a teardrop or not.
    :param td_curve_segcount: The number of segments used to approximate a curved teardrop shape.
    :param td_on_pad_in_zone: Whether teardrops are allowed on pads within zones or not.
    :param td_onpadsmd: Whether if teardrops are allowed on SMD pads or not.
    :param td_onroundshapesonly: Whether teardrops are only applied to round shapes or not.
    :param td_ontrackend: Whether teardrops are applied on track ends or not.
    :param td_onviapad: Whether teardrops are allowed on via pads or not.
    """

    td_allow_use_two_tracks: Optional[bool]
    td_curve_segcount: Optional[int]
    td_on_pad_in_zone: Optional[bool]
    td_onpadsmd: Optional[bool]
    td_onroundshapesonly: Optional[bool]
    td_ontrackend: Optional[bool]
    td_onviapad: Optional[bool]


class TeardropParameter(BaseModel):
    """
    The parameters used to control the shape and size of teardrops.

    :param td_curve_segcount: The number of segments used to approximate a curved teardrop shape.
    :param td_height_ratio: The ratio of teardrop height to pad size.
    :param td_length_ratio: The ratio of teardrop length to pad size.
    :param td_maxheight: The maximum allowed height of a teardrop.
    :param td_maxlen: The maximum allowed length of a teardrop.
    :param td_target_name: The name of the target layer for teardrops.
    :param td_width_to_size_filter_ratio: The ratio of teardrop width to pad size for filtering.
    """

    td_curve_segcount: int
    td_height_ratio: float
    td_length_ratio: float
    td_maxheight: float
    td_maxlen: float
    td_target_name: str
    td_width_to_size_filter_ratio: Optional[float]


class ViaDimension(BaseModel):
    """
    The diameter and drill size of a via.

    :param diameter: The diameter of the via pad.
    :param drill: The drill size of the via hole.
    """

    diameter: float
    drill: float


class DesignSettings(BaseModel):
    """
    Various settings used for configuring the design process.

    :param apply_defaults_to_field: Whether default values should be applied to fields or not.
    :param apply_defaults_to_shapes: Whether default values should be applied to shapes or not.
    :param apply_defaults_to_fp_text: Whether default values should be applied to footprint text or not.
    :param defaults: An Instance of :py:class:`Defaults`.
    :param diff_pair_dimensions: A list of differential pair dimension settings.
    :param drc_exclusions: A list of DRC (Design Rule Checks) exclusion rules.
    :param meta: An instance of :py:class:`Meta`.
    :param rule_severities: Dictionary defining severities for different design rules.
    :param rule_severitieslegacy_courtyards_overlap: Whether legacy courtyard overlap severity is used  or not.
    :param rule_severitieslegacy_no_courtyard_defined: Whether legacy no courtyard defined severity is used  or not.
    :param rules: An instance of :py:class:`Rules`.
    :param teardrop_options: List of :py:class:`TeardropOption` defining teardrop options.
    :param teardrop_parameters: List of :py:class:`TeardropParameter` defining teardrop parameters.
    :param track_widths: List of allowed track (trace) widths.
    :param via_dimensions: List of :py:class:`ViaDimension` defining via dimensions.
    :param zones_allow_external_fillets: Whether external fillets are allowed on zones or not.
    :param zones_use_no_outline: Whether zones are allowed without an outline or not.
    """

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
    """
    A PCB design within the context of a Cvpcb file.

    :param field_3dviewports: A list of 3D viewport definitions.
    :param design_settings: An instance of :py:class:`DesignSettings`.
    :param layer_presets: A list of layer preset definitions.
    :param viewports: A list of viewport definitions.
    """

    field_3dviewports: Optional[list] = Field(default=None, alias="3dviewports")
    design_settings: DesignSettings
    layer_presets: list
    viewports: Optional[list]


class Cvpcb(BaseModel):
    """
    The root element of a Cvpcb file containing a PCB design.

    :param equivalence_files: A list of equivalence files associated with the PCB design.
    """

    equivalence_files: list


class Erc(BaseModel):
    """
    Electrical Rule Checking (ERC) settings.

    :param erc_exclusions: A list of ERC exclusion rules.
    :param meta: An instance of :py:class:`Meta`.
    :param pin_map: A list of lists representing pin mappings.
    :param rule_severities: Dictionary defining severities for different ERC rules.
    """

    erc_exclusions: list
    meta: Meta
    pin_map: list[list[int]]
    rule_severities: dict[str, Any]


class Libraries(BaseModel):
    """
    Library settings for footprints and symbols.

    :param pinned_footprint_libs: List of pinned footprint libraries.
    :param pinned_symbol_libs: List of pinned symbol libraries.
    """

    pinned_footprint_libs: list
    pinned_symbol_libs: list


class Class(BaseModel):
    """
    The properties associated with a design class in the PCB layout.

    :param bus_width: The width of a bus (multiple connected tracks).
    :param clearance: The clearance between objects
    :param diff_pair_gap: The gap between tracks in a differential pair.
    :param diff_pair_via_gap: The gap between vias in a differential pair.
    :param diff_pair_width: The width of tracks in a differential pair.
    :param line_style: The line style used.
    :param microvia_diameter: The diameter of microvias.
    :param microvia_drill: The drill size for microvias.
    :param name: The name of the design class.
    :param pcb_color: The color used on the PCB layout.
    :param schematic_color: The color used on the schematic.
    :param track_width: The default track width.
    :param via_diameter: The diameter of vias.
    :param via_drill: The drill size for vias.
    :param wire_width: The width of wires.
    """

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
    """
    A pattern for matching netclasses in the PCB design.

    :param netclass: The net class name to match.
    :param pattern: A regular expression pattern for matching nets within the net class.
    """

    netclass: str
    pattern: str


class NetSettings(BaseModel):
    """
    Various settings related to nets (electrical connections) in the PCB design.

    :param classes: A list of :py:class:`Class` objects.
    :param meta: An instance of :py:class:`Meta`.
    :param net_colors: Dictionary mapping net names to their corresponding colors.
    :param netclass_assignments: Dictionary mapping net names to their assigned net classes.
    :param netclass_patterns: A list of :py:class:`NetclassPattern` objects.
    """

    classes: list[Class]
    meta: Meta
    net_colors: Optional[dict[str, str]]
    netclass_assignments: Optional[dict[str, str]]
    netclass_patterns: Optional[list[NetclassPattern]]


class LastPaths(BaseModel):
    """
    Stores the paths to various generated files associated with the PCB design.

    :param gencad: The path to the generated GenCAD file.
    :param idf: The path to the generated IDF file.
    :param netlist: The path to the generated netlist file.
    :param specctra_dsn: The path to the generated Specctra DSN file.
    :param step: The path to the generated STEP file.
    :param vrml: The path to the generated VRML file.
    """

    gencad: str
    idf: str
    netlist: str
    specctra_dsn: str
    step: str
    vrml: str


class Pcbnew(BaseModel):
    """
    The PCBnew section within a Cvpcb file.

    :param last_paths: An instance of :py:class:`LastPaths`.
    :param page_layout_descr_file: The path to the page layout description file.

    """

    last_paths: LastPaths
    page_layout_descr_file: str


class Drawing(BaseModel):
    """
    The settings related to the visual appearance of the PCB schematic drawing.

    :param dashed_lines_dash_length_ratio: The ratio of dash length to gap length for dashed lines.
    :param dashed_lines_gap_length_ratio: The ratio of gap length to dash length for dashed lines.
    :param default_line_thickness: The default thickness for lines in the schematic.
    :param default_text_size: The default size for text in the schematic.
    :param default_bus_thickness: The default thickness for buses (multiple connected wires) in the schematic.
    :param default_junction_size: The default size for junctions (connection points) in the schematic.
    :param default_wire_thickness: The default thickness for wires in the schematic.
    :param field_names: List of field names displayed in the schematic.
    :param intersheets_ref_own_page: Whether intersheet references point to the same page or not.
    :param intersheets_ref_prefix: The prefix string used for intersheet references.
    :param intersheets_ref_short: Whether intersheet references are shortened or not.
    :param intersheets_ref_show: Whether if intersheet references are displayed or not.
    :param intersheets_ref_suffix: The suffix string used for intersheet references.
    :param junction_size_choice: The choice for the default junction size (e.g., absolute, relative).
    :param label_size_ratio: The ratio of label size to element size.
    :param pin_symbol_size: The size of pin symbols in the schematic.
    :param text_offset_ratio: The ratio of text offset to element size.
    """

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
    """
    The settings related to NGSPICE simulation for the PCB design.

    :param fix_include_paths: Whether to fix include paths for NGSPICE simulations or not.
    :param fix_passive_vals: Whether to fix passive component values for NGSPICE simulations or not.
    :param meta: An instance of :py:class:`Meta`.
    :param model_mode: The mode used for NGSPICE model handling.
    :param workbook_filename: The file name of the NGSPICE workbook.
    """

    fix_include_paths: Optional[bool]
    fix_passive_vals: Optional[bool]
    meta: Optional[Meta]
    model_mode: Optional[int]
    workbook_filename: Optional[str]


class ProjectSchematic(BaseModel):
    """
    The settings related to the project schematic associated with the project file.

    :param annotate_start_num: The starting number for schematic annotations.
    :param drawing: An instance of :py:class:`Drawing`.
    :param legacy_lib_dir: Directory containing legacy schematic symbol libraries.
    :param legacy_lib_list: A list of legacy schematic symbol libraries to use.
    :param meta: Reference to a Meta object containing PCB layout metadata.
    :param net_format_name: The name of the netlist format for the schematic.
    :param ngspice: An instance of :py:class:`Ngspice`.
    :param page_layout_descr_file: The path to the schematic page layout description file.
    :param plot_directory: Directory for storing simulation plots.
    :param spice_adjust_passive_values: Whether to adjust passive component values for SPICE simulation or not.
    :param spice_current_sheet_as_root: Whether the current schematic sheet is considered the root for SPICE simulation or not.
    :param spice_external_command: External command to run for SPICE simulation.
    :param spice_model_current_sheet_as_root: Whether the current schematic sheet is considered the root for NGSPICE model loading or not.
    :param spice_save_all_currents: Whether to save all currents during SPICE simulation or not.
    :param spice_save_all_voltages: Whether to save all voltages during SPICE simulation or not.
    :param subpart_first_id: The starting ID for subparts in the schematic.
    :param subpart_id_separator: The character used as separator for subpart IDs.
    """

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
    """
    A project sheet within a KiCad project.

    :param uuid: The Universally Unique Identifier (UUID) of the project sheet.
    :param name: The name of the project sheet.
    """

    uuid: UUID
    name: str


class KicadProject(BaseModel):
    """
    The entire KiCad project structure as defined in a Cvpcb file.

    :param board: An instance of :py:class:`Board`.
    :param boards: A list of board definitions.
    :param cvpcb: An instance of :py:class:`Cvpcb`.
    :param erc: An instance of :py:class:`Erc`.
    :param libraries: An instance of :py:class:`Libraries`.
    :param meta: An instance of :py:class:`Meta`.
    :param net_settings: An instance of :py:class:`NetSettings`.
    :param pcbnew: An instance of :py:class:`Pcbnew`.
    :param schematic: An instance of :py:class:`ProjectSchematic`.
    :param sheets: A list of project sheets.
    :param text_variables: A dictionary of text variables.

    """

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
