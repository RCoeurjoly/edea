"""
Dataclasses describing the contents of .kicad_sch files.
"""

import pathlib
from dataclasses import field
from typing import Annotated, Any, ClassVar, Literal, Optional
from uuid import UUID, uuid4

from pydantic import validator
from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.base import CustomizationDataTransformRegistry
from edea.kicad.color import Color
from edea.kicad.common import Image, Paper, PaperStandard, TitleBlock, VersionError
from edea.kicad.schematic.base import KicadSchExpr
from edea.kicad.schematic.shapes import (
    Arc,
    Circle,
    Fill,
    FillColor,
    FillSimple,
    Polyline,
    Pts,
    Rectangle,
    Stroke,
)
from edea.kicad.schematic.symbol import Effects, LibSymbol, Property


@dataclass(config=PydanticConfig, eq=False)
class PinAssignment(KicadSchExpr):
    number: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    uuid: UUID = field(default_factory=uuid4)
    alternate: Optional[str] = None
    kicad_expr_tag_name: ClassVar[Literal["pin"]] = "pin"


@dataclass(config=PydanticConfig, eq=False)
class DefaultInstance(KicadSchExpr):
    """
    Default component instance associated with the symbol.

    :param reference: Reference designator for the component.
    :param unit: Which unit in the symbol library definition that the schematic symbol represents.
    :param value: The component value.
    :param footprint: The footprint associated with the component.
    """

    reference: Annotated[str, m("kicad_always_quotes")]
    unit: int = 1
    value: Annotated[str, m("kicad_always_quotes")] = ""
    footprint: Annotated[str, m("kicad_always_quotes")] = ""
    kicad_expr_tag_name: ClassVar[Literal["default_instance"]] = "default_instance"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstancePath(KicadSchExpr):
    """
    A path between components within a KiCad schematic project.

    :param name: Reference designator for the component in the path.
    :param reference: Reference designator for the starting point of the path.
    :param unit: Which unit in the symbol library definition that the schematic symbol represents..
    :cvar kicad_expr_tag_name: The KiCad expression tag name for "path" element.
    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    reference: Annotated[str, m("kicad_always_quotes")]
    unit: int
    kicad_expr_tag_name: ClassVar[Literal["path"]] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstanceProject(KicadSchExpr):
    """
    A symbol usage information for a specific project within a KiCad schematic.

    :param name: The project name where the symbol is used.
    :param paths: A list of :py:class:`SymbolUseInstancePath` objects defining connections within the project.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for for this element ("project").
    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    paths: list[SymbolUseInstancePath] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["project"]] = "project"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUseInstances(KicadSchExpr):
    """
    A symbol usage information across different projects within a KiCad schematic.

    :param projects: A list of :py:class:`SymbolUseInstanceProject` objects defining symbol usage details for each project.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for for this element  ("instances").
    """

    projects: list[SymbolUseInstanceProject] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["instances"]] = "instances"


@dataclass(config=PydanticConfig, eq=False)
class SymbolUse(KicadSchExpr):
    """
    A symbol instance placed within a KiCad schematic.

    :param lib_name: The library name where the symbol is defined (`KiCad library \
        identifier <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_library_identifier>`_).
    :param lib_id: The library symbol ID.
    :param at: The X-Y coordinates and rotation angle of the symbol instance.
    :param mirror: Optional mirroring applied to the symbol.
    :param unit: Which unit in the symbol library definition that the schematic symbol represents.
    :param convert: The conversion factor for the symbol.
    :param exclude_from_sim: Whether the symbol is excluded from simulation.
    :param in_bom: Whether the symbol should be included in the Bill of Materials or not.
    :param on_board: Whether the symbol is exported to the board via the netlist.
    :param dnp: "Do Not Populate" flag for the symbol.
    :param fields_autoplaced: Whether the symbol fields are automatically placed.
    :param uuid: The unique identifier for the symbol instance.
    :param default_instance: Default component instance associated with the symbol.
    :param properties: A list of property objects associated with the symbol.
    :param pins: A list of :py:class:`PinAssignment` objects defining pin assignments for the symbol.
    :param instances: Nested :py:class:`SymbolUseInstances` object defining symbol usage within hierarchical symbols.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("symbol").

    .. note::
        The `exclude_from_sim` field was added in 20231120 (KiCad 8).
    """

    lib_name: Optional[str] = None
    lib_id: Annotated[str, m("kicad_always_quotes")] = ""
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    mirror: Literal["x", "y", None] = None
    unit: int = 1
    convert: Optional[int] = None
    exclude_from_sim: Annotated[
        Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")
    ] = None
    in_bom: Annotated[bool, m("kicad_bool_yes_no")] = True
    on_board: Annotated[bool, m("kicad_bool_yes_no")] = True
    dnp: Annotated[bool, m("kicad_bool_yes_no")] = False
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    uuid: UUID = field(default_factory=uuid4)
    default_instance: Optional[DefaultInstance] = None
    properties: list[Property] = field(default_factory=list)
    pins: list[PinAssignment] = field(default_factory=list)
    instances: Optional[SymbolUseInstances] = None
    kicad_expr_tag_name: ClassVar[Literal["symbol"]] = "symbol"

    @validator("properties")
    @classmethod
    def _validate_properties(cls, properties):
        """
        :raises ValueError: If "reference" or "value" properties are missing.
        """
        keys = [prop.key for prop in properties]
        if "Reference" not in keys:
            raise ValueError(
                '"reference" (Reference) is missing from symbol properties'
            )
        if "Value" not in keys:
            raise ValueError('"value" (Value) is missing from symbol properties')
        return properties

    reference: Annotated[str, m("exclude_from_files")]  # type: ignore
    value: Annotated[str, m("exclude_from_files")]  # type: ignore

    @property
    def reference(self) -> str:
        """
        Retrieves the "Reference" value from the associated properties.

        :raises KeyError: If the "Reference" property is not found.
        """
        for prop in self.properties:
            if prop.key == "Reference":
                return prop.value
        raise KeyError("Reference not found")

    @reference.setter
    def reference(self, value: str):
        """
        Updates the "Reference" value within the associated properties.

        :param value: The new value to be assigned to the "Reference" property.
        """
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Reference":
                prop.value = value
                break
        else:
            self.properties.append(
                Property(
                    key="Reference",
                    value=value,
                )
            )

    @property
    def value(self) -> str:
        """
        Retrieves the "Value" value from the associated properties.

        :raises KeyError: If the "Value" property is not found.
        """
        for prop in self.properties:
            if prop.key == "Value":
                return prop.value
        raise KeyError("Value not found")

    @value.setter
    def value(self, value: str):
        """
        Updates the "Value" value within the associated properties.

        :param value: New value to be assigned to the "Value" property.
        """
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Value":
                prop.value = value
                break
        else:
            self.properties.append(
                Property(
                    key="Value",
                    value=value,
                )
            )


@dataclass(config=PydanticConfig, eq=False)
class Wire(KicadSchExpr):
    """
    A wire element within a KiCad schematic.

    `KiCad wire <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_wire_and_bus_section>`_

    :param pts: the list of X-Y coordinates of start and end points of the wire.
    :param stroke: How the wire or bus is drawn.
    :param uuid: The wire id.
    """

    pts: Pts = field(default_factory=Pts)
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["wire"]] = "wire"


@dataclass(config=PydanticConfig, eq=False)
class Junction(KicadSchExpr):
    """
    A junction (connection point) within a KiCad schematic.

    `KiCad junction <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_junction_section>`_

    :param at: The X-Y coordinates of the junction.
    :param diameter: The diameter of the junction.
    :param color: RGBA color.
    :param uuid: The junction id.
    """

    at: tuple[float, float]
    diameter: float = 0
    color: Color = (0, 0, 0, 0.0)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["junction"]] = "junction"


@dataclass(config=PydanticConfig, eq=False)
class NoConnect(KicadSchExpr):
    """
    A "No Connect" element within a KiCad schematic, indicating an unused pin.

    `KiCad no_connect <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_no_connect_section>`_

    :param at: The X-Y coordinates of the "No Connect" symbol.
    :param uuid: The unused junction id.
    """

    at: tuple[float, float]
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["no_connect"]] = "no_connect"


@dataclass(config=PydanticConfig, eq=False)
class LocalLabel(KicadSchExpr):
    """
    A local label element within a KiCad schematic.

    `KiCad local label <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_local_label_section>`_

    :param text: The string that defines the label.
    :param at: The X-Y coordinates and rotation angle of the label.
    :param fields_autoplaced: Whether the label fields are automatically placed.
    :param effects: How the label text is drawn.
    :param properties: A list of property objects associated with the label.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("label").
    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["label", "text"]] = "label"


@dataclass(config=PydanticConfig, eq=False)
class Text(LocalLabel):
    """
    A simple text element within a KiCad schematic.

    :param exclude_from_sim: Whether the text is excluded from simulation.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("text").

    .. note::
        The `exclude_from_sim` field was added in 20231120 (KiCad 8).

    """

    exclude_from_sim: Annotated[
        Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")
    ] = None
    kicad_expr_tag_name = "text"


@dataclass(config=PydanticConfig, eq=False)
class TextBox(KicadSchExpr):
    """
    A text box element within a KiCad schematic.

    :param text: The text content of the box.
    :param at: The X-Y coordinates and rotation angle of the text box.
    :param size: The size of the text box.
    :param exclude_from_sim: Whether the text box is excluded from simulation.
    :param stroke: The line width and style of the text box.
    :param fill: How the text box is filled.
    :param effects: How the text box is displayed.
    :param uuid: The unique identifier for the text box.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("text_box").

    .. note::
        The `exclude_from_sim` field was added in 20231120 (KiCad 8).

    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    size: tuple[float, float]
    exclude_from_sim: Annotated[
        Optional[bool], m("kicad_bool_yes_no", "kicad_omits_default")
    ] = None
    stroke: Stroke = field(default_factory=Stroke)
    fill: Fill = field(default_factory=FillSimple)
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["text_box"]] = "text_box"


class LabelShape(StrEnum):
    """
    Different shapes allowed for global labels in KiCad schematics.
    """

    # pylint: disable=duplicate-code
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRI_STATE = "tri_state"
    PASSIVE = "passive"


@dataclass(config=PydanticConfig, eq=False)
class GlobalLabel(KicadSchExpr):
    """
    A global label element within a KiCad schematic.

    `KiCad global label <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_global_label_section>`_

    :param text: The string that defines the global label.
    :param shape: The way the global label is drawn.
    :param at: The X-Y coordinates and rotation angle of the label.
    :param fields_autoplaced: A flag that indicates that any properties associated with the global label have been place automatically.
    :param effects: How the global label text is drawn.
    :param uuid: The global label id.
    :param properties: The properties of the global label.
    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["global_label"]] = "global_label"


@dataclass(config=PydanticConfig, eq=False)
class HierarchicalLabel(KicadSchExpr):
    """
    A hierarchical label element within a KiCad schematic.

    `KiCad hierarchical label <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_hierarchical_label_section>`_

    :param text: The string that defines the hierarchical label.
    :param shape: The way the hierarchical label is drawn.
    :param at: The X-Y coordinates and rotation angle of the hierarchical label.
    :param fields_autoplaced: A flag that indicates that any properties associated with \
        the hierarchical label have been place automatically.
    :param effects: How the hierarchical label text is drawn.
    :param uuid: The hierarchical label id.
    :param properties: he properties of the hierarchical label.
    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    shape: LabelShape = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["hierarchical_label"]] = "hierarchical_label"


@dataclass(config=PydanticConfig, eq=False)
class NetclassFlag(KicadSchExpr):
    """
    A net class flag element within a KiCad schematic.

    :param text: The text content of the net class flag.
    :param length: The length of the net class flag.
    :param shape: The way the net class flag is drawn.
    :param at: The X-Y coordinates and rotation angle of the the net class flag's position.
    :param fields_autoplaced: Whether to auto place the net class flag or not.
    :param effects: How the net class flag is drawn.
    :param uuid: The net class flag id.
    :param properties: The properties of the the net class flag.
    """

    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    length: float
    shape: Literal["rectangle", "round", "diamond", "dot"]
    at: tuple[float, float, Literal[0, 90, 180, 270]]
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = False
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["netclass_flag"]] = "netclass_flag"


@dataclass(config=PydanticConfig, eq=False)
class LibSymbols(KicadSchExpr):
    """
    A collection of library symbol references within a KiCad schematic.

    :param symbols: A list of :py:class:`edea.kicad.schematic.symbol.LibSymbol` objects defining individual symbol references.
    """

    symbols: list[LibSymbol] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["lib_symbols"]] = "lib_symbols"


@dataclass(config=PydanticConfig, eq=False)
class SymbolInstancesPath(KicadSchExpr):
    """
    A path within a hierarchical symbol referencing another symbol within a KiCad schematic.

    `KiCad instance path <https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/index.html#_instance_path>`_

    :param path: The path string specifying the hierarchical location.
    :param reference: The reference name of the symbol being referenced.
    :param unit: An integer ordinal that defines the symbol unit for the symbol instance. \
        For symbols that do not define multiple units, this will always be 1.
    :param value: The value of the symbol instance.
    :param footprint: The footprint associated with the symbol instance.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("path").
    """

    path: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    reference: Annotated[str, m("kicad_always_quotes")]
    unit: int
    value: Annotated[str, m("kicad_always_quotes")]
    footprint: Annotated[str, m("kicad_always_quotes")]
    kicad_expr_tag_name: ClassVar[Literal["path"]] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SymbolInstances(KicadSchExpr):
    """
    A collection of symbol instances within a KiCad schematic.

    :param paths: A list of :py:class:`SymbolInstancesPath` objects defining individual symbol instance paths.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("instances").
    """

    paths: list[SymbolInstancesPath] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["symbol_instances"]] = "symbol_instances"


@dataclass(config=PydanticConfig, eq=False)
class SheetPin(KicadSchExpr):
    """
    A pin element on a sheet within a KiCad schematic.

    :param name: The name of the pin.
    :param shape: The shape of the pin label.
    :param at: The X-Y coordinates and rotation angle of the pin.
    :param effects: Reference to an `Effects` object defining text effects.
    :param uuid: The unique identifier (UUID) for the pin element.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("pin").
    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    shape: Annotated[LabelShape, m("kicad_no_kw")] = LabelShape.BIDIRECTIONAL
    at: tuple[float, float, Literal[0, 90, 180, 270]] = (0, 0, 0)
    effects: Effects = field(default_factory=Effects)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["pin"]] = "pin"


@dataclass(config=PydanticConfig, eq=False)
class SheetInstancesPath(KicadSchExpr):
    """
    A path within a hierarchical schematic referencing another sheet.

    :param name: The name of the referenced sheet.
    :param page: The page of the referenced sheet within the project.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("path").
    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    page: Annotated[str, m("kicad_always_quotes")]
    kicad_expr_tag_name: ClassVar[Literal["path"]] = "path"


@dataclass(config=PydanticConfig, eq=False)
class SheetInstances(KicadSchExpr):
    """
    A collection of sheet instances within a hierarchical KiCad schematic.

    :param paths: A list of `SheetInstancesPath` objects defining individual sheet instance paths.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("sheet_instances").
    """

    paths: list[SheetInstancesPath] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["sheet_instances"]] = "sheet_instances"


@dataclass(config=PydanticConfig, eq=False)
class SubSheetInstanceProject(KicadSchExpr):
    """
    A sub-sheet instance referencing another project within a KiCad schematic.

    :param name: The name of the referenced project.
    :param paths: A list of `SheetInstancesPath` objects defining paths within the referenced project.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("project").
    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    paths: list[SheetInstancesPath] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["project"]] = "project"


@dataclass(config=PydanticConfig, eq=False)
class SubSheetInstances(KicadSchExpr):
    """
    A sub-sheet instance within a KiCad schematic.

    :param projects: A list of `SubSheetInstanceProject` objects defining projects within the sub-sheet.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("instances").
    """

    projects: list[SubSheetInstanceProject] = field(default_factory=list)
    kicad_expr_tag_name: ClassVar[Literal["instances"]] = "instances"


@dataclass(config=PydanticConfig, eq=False, kw_only=True)
class Sheet(KicadSchExpr):
    """
    A sheet element within a KiCad schematic.

    :param at: The X-Y coordinates of the sheet's top-left corner.
    :param size: The size of the sheet.
    :param fields_autoplaced: Whether sheet fields are automatically placed or not.
    :param stroke: Instance of `Stroke` object defining the sheet outline style.
    :param fill: Instance of `FillColor` object defining the sheet fill style.
    :param uuid: The unique identifier (UUID) for the sheet element.
    :param properties: A list of `Property` objects defining sheet properties.
    :param pins: A list of `SheetPin` objects defining pins on the sheet.
    :param instances: Instance of SubSheetInstances object for hierarchical nesting.
    :param name: Internal property to access the sheet name retrieved from "Sheetname" property within `properties`.
    :param file: Internal property to access the sheet file path retrieved from "Sheetfile" property within `properties`.
    """

    at: tuple[float, float] = (15.24, 15.24)
    size: tuple[float, float] = (15.24, 15.24)
    fields_autoplaced: Annotated[bool, m("kicad_kw_bool_empty")] = True
    stroke: Stroke = field(default_factory=Stroke)
    fill: FillColor = field(default_factory=FillColor)
    uuid: UUID = field(default_factory=uuid4)
    properties: list[Property] = field(default_factory=list)
    pins: list[SheetPin] = field(default_factory=list)
    instances: Optional[SubSheetInstances] = None
    kicad_expr_tag_name: ClassVar[Literal["sheet"]] = "sheet"

    @validator("properties")
    @classmethod
    def _validate_properties(cls, properties):
        """
        :raises ValueError: If required sheet properties "Sheetname" and "Sheetfile" are missing from the 'properties' list.
        """
        keys = [prop.key for prop in properties]
        if "Sheetname" not in keys:
            raise ValueError('"name" (Sheetname) is missing from sheet properties')
        if "Sheetfile" not in keys:
            raise ValueError('"file" (Sheetfile) is missing from sheet properties')
        return properties

    name: Annotated[str, m("exclude_from_files")]  # type: ignore
    file: Annotated[pathlib.Path, m("exclude_from_files")]  # type: ignore

    @property
    def name(self) -> str:
        """
        Retrieves the sheet name by searching for the "Sheetname" property within 'properties'.

        :returns prop.value: The sheet name as a string.
        :raises KeyError: If "Sheetname" property is not found.
        """
        for prop in self.properties:
            if prop.key == "Sheetname":
                return prop.value
        raise KeyError("Sheetname not found")

    @name.setter
    def name(self, value: str):
        """
        Sets the sheet name by updating the "Sheetname" property within 'properties'.

        :param value: The new sheet name as a string.
        """
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Sheetname":
                prop.value = value
                break
        else:
            self.properties.append(
                Property(
                    key="Sheetname",
                    value=value,
                    at=(self.at[0], self.at[1] - 0.7116, 0),
                    effects=Effects(justify=["left", "bottom"]),
                )
            )

    @property
    def file(self) -> pathlib.Path:
        """
        Retrieves the sheet file path by searching for the "Sheetfile" property within 'properties'.

        :raises KeyError: If "Sheetfile" property is not found.
        :returns: The sheet file path as a pathlib.Path object.
        """
        for prop in self.properties:
            if prop.key == "Sheetfile":
                return pathlib.Path(prop.value)
        raise KeyError("Sheetfile not found")

    @file.setter
    def file(self, value: pathlib.Path):
        """
        Sets the sheet file path by updating the "Sheetfile" property within 'properties'.

        :param value: The new sheet file path as a pathlib.Path object.
        """
        # when it's missing in __init__ it's a "property" object, we just
        # ignore that
        if isinstance(value, property):
            return
        for prop in self.properties:
            if prop.key == "Sheetfile":
                prop.value = str(value)
                break
        else:
            self.properties.append(
                Property(
                    key="Sheetfile",
                    value=str(value),
                    at=(self.at[0], self.at[1] + self.size[1] + 0.5846, 0),
                    effects=Effects(justify=["left", "top"]),
                )
            )


@dataclass(config=PydanticConfig, eq=False)
class BusEntry(KicadSchExpr):
    """
    A bus entry element within a KiCad schematic.

    :param at: The X-Y coordinates of the bus entry.
    :param size: The X and Y distance of the end point from the position of the bus entry.
    :param stroke: How the bus entry is drawn.
    :param uuid: The unique identifier (UUID) for the bus entry element.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("bus_entry").
    """

    at: tuple[float, float]
    size: tuple[float, float]
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["bus_entry"]] = "bus_entry"


@dataclass(config=PydanticConfig, eq=False)
class Bus(KicadSchExpr):
    """
    A bus element within a KiCad schematic.

    :param pts: The list of X and Y coordinates of start and end points of the bus.
    :param stroke: How the bus is drawn.
    :param uuid: The unique identifier (UUID) for the bus.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("bus").
    """

    pts: Annotated[Pts, m("kicad_omits_default")] = field(
        default_factory=Pts,
    )
    stroke: Stroke = field(default_factory=Stroke)
    uuid: UUID = field(default_factory=uuid4)
    kicad_expr_tag_name: ClassVar[Literal["bus"]] = "bus"


@dataclass(config=PydanticConfig, eq=False)
class BusAlias(KicadSchExpr):
    """
    A bus alias element within a KiCad schematic.

    :param name: The name of the bus alias.
    :param members: A list of bus member names associated with the alias.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("bus_alias").
    """

    name: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")]
    members: Annotated[list[str], m("kicad_always_quotes")] = field(
        default_factory=list,
    )
    kicad_expr_tag_name: ClassVar[Literal["bus_alias"]] = "bus_alias"


SUPPORTED_KICAD_SCH_VERSIONS_TYPE = Literal["20231120", "20230121"]


@dataclass(config=PydanticConfig, eq=False)
class Schematic(KicadSchExpr, metaclass=CustomizationDataTransformRegistry):
    """
    A KiCad schematic file structure.

    :param version: The KiCad schematic file format version.
    :param generator: The schematic file generator software.
    :param generator_version: The version of the schematic file generator software.
    :param uuid: The unique identifier (UUID) for the schematic file.
    :param uuid: The unique identifier (UUID) for the schematic file.
    :param paper: The schematic sheet properties.
    :param title_block: Title block information.
    :param lib_symbols: Library symbol references.
    :param arcs: Arcs within the schematic.
    :param circles: Circles within the schematic.
    :param sheets: Ondividual sheets within the schematic.
    :param symbols: Symbol instances within the schematic.
    :param rectangles: Rectangles within the schematic.
    :param wires: Wires within the schematic.
    :param polylines: Polylines within the schematic.
    :param buses: Buses within the schematic.
    :param images: Images within the schematic.
    :param junctions: Junctions (connection points) within the schematic.
    :param no_connects: Unconnected pins within the schematic.
    :param bus_entries: Bus entries within the schematic.
    :param text_items:  Text elements within the schematic.
    :param text_boxes: Text boxes within the schematic.
    :param labels: Local labels within the schematic.
    :param hierarchical_labels: Hierarchical labels within the schematic.
    :param global_labels: Global labels within the schematic.
    :param netclass_flags: List of `NetclassFlag` objects defining net class flags within the schematic.
    :param bus_aliases: Bus aliases within the schematic.
    :param sheet_instances: Sheet instances.
    :param symbol_instances: Symbol instances within the schematic.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("kicad_sch").

    .. note::
        The `generator_version`, and `uuid` fields were added in 20231120 (KiCad 8).

    """

    version: SUPPORTED_KICAD_SCH_VERSIONS_TYPE = "20231120"

    @validator("version")
    @classmethod
    def check_version(cls, v: Any) -> SUPPORTED_KICAD_SCH_VERSIONS_TYPE:
        """
        Checks KiCad schematic file format version.

        :returns v: The version number.
        :raises VersionError: If the version format isn't supported.
        """
        if v == "20230121" or v == "20231120":
            return v
        raise VersionError(
            "Only the stable KiCad 7 and KiCad 8 schematic file formats i.e. ('20230121', and '20231120') are"
            f" supported. Got '{v}'. Please open and re-save the file with"
            " KiCad 7 (or a newer version) if you can."
        )

    generator: Annotated[str, m("kicad_always_quotes")] = "edea"
    generator_version: Annotated[
        Optional[str], m("kicad_always_quotes", "kicad_omits_default")
    ] = None
    uuid: Optional[UUID] = None
    paper: Paper = field(default_factory=PaperStandard)
    title_block: Optional[TitleBlock] = None
    lib_symbols: LibSymbols = field(default_factory=LibSymbols)
    arcs: list[Arc] = field(default_factory=list)
    circles: list[Circle] = field(default_factory=list)
    sheets: list[Sheet] = field(default_factory=list)
    symbols: list[SymbolUse] = field(default_factory=list)
    rectangles: list[Rectangle] = field(default_factory=list)
    wires: list[Wire] = field(default_factory=list)
    polylines: list[Polyline] = field(default_factory=list)
    buses: list[Bus] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    junctions: list[Junction] = field(default_factory=list)
    no_connects: list[NoConnect] = field(default_factory=list)
    bus_entries: list[BusEntry] = field(default_factory=list)
    text_items: list[Text] = field(default_factory=list)
    text_boxes: list[TextBox] = field(default_factory=list)
    labels: list[LocalLabel] = field(default_factory=list)
    hierarchical_labels: list[HierarchicalLabel] = field(default_factory=list)
    global_labels: list[GlobalLabel] = field(default_factory=list)
    netclass_flags: list[NetclassFlag] = field(default_factory=list)
    bus_aliases: list[BusAlias] = field(default_factory=list)
    sheet_instances: SheetInstances | None = field(default=None)
    symbol_instances: Annotated[SymbolInstances, m("kicad_omits_default")] = field(
        default_factory=SymbolInstances,
    )

    kicad_expr_tag_name: ClassVar[Literal["kicad_sch"]] = "kicad_sch"
