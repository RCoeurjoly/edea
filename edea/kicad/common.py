from dataclasses import field
from typing import Annotated, ClassVar, Literal, Optional, Union
from uuid import UUID, uuid4

from pydantic.dataclasses import dataclass

from edea.kicad._config import PydanticConfig
from edea.kicad._fields import make_meta as m
from edea.kicad._str_enum import StrEnum
from edea.kicad.base import KicadExpr
from edea.kicad.color import Color


class StrokeType(StrEnum):
    """
    Available stroke types that can be used for lines, outlines, etc.

    `KiCad stroke definition <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_stroke_definition>`_
    """

    DEFAULT = "default"
    """
    Stroke type.
    """
    DASH = "dash"
    """
    Evenly spaced dashes.
    """
    DASH_DOT = "dash_dot"
    """
    Alternating dashes and dots.
    """
    DASH_DOT_DOT = "dash_dot_dot"
    """
    Alternating dashes and double dots.
    """
    DOT = "dot"
    """
    Evenly spaced dots.
    """
    SOLID = "solid"
    """
    Continuous solid.
    """


@dataclass(config=PydanticConfig, eq=False)
class Stroke(KicadExpr):
    """
    Properties of a stroke used within KiCad expressions.

    `KiCad stroke definition <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_stroke_definition>`_

    :param width: The line width of the graphic object.
    :param type: The line style of the graphic object.
    :param color: The red, green, blue, and alpha color settings.

    """

    width: float = 0
    type: StrokeType = StrokeType.DEFAULT
    color: Annotated[Color, m("kicad_omits_default")] = (0, 0, 0, 0.0)


class PaperFormat(StrEnum):
    """
    Various standard paper formats like A series A0, A1, B series, etc.

    `KiCad paper format <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_page_settings>`_
    """

    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    US_LETTER = "USLetter"
    US_LEGAL = "USLegal"
    US_LEDGER = "USLedger"


class PaperOrientation(StrEnum):
    """
    The two common paper shown modes: landscape and portrait.

    `KiCad paper format <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_page_settings>`_

    """

    LANDSCAPE = ""
    """
    The default value (empty string), represents horizontal orientation.
    """
    PORTRAIT = "portrait"
    """
    Represents vertical orientation.
    """


@dataclass(config=PydanticConfig, eq=False)
class PaperUser(KicadExpr):
    """
    A custom KiCad paper size definition.

    :param format: Always set to "User" to indicate a custom format.
    :param width: The width of the paper in KiCad units.
    :param height: The height of the paper in KiCad units
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("paper").
    """

    format: Annotated[Literal["User"], m("kicad_no_kw", "kicad_always_quotes")] = "User"
    width: Annotated[float, m("kicad_no_kw")] = 0
    height: Annotated[float, m("kicad_no_kw")] = 0
    kicad_expr_tag_name: ClassVar[Literal["paper"]] = "paper"

    def as_dimensions_mm(self) -> tuple[float, float]:
        """
        Calculates the paper dimensions based on the user-defined width and height.

        :returns: A tuple containing the width and height of the paper.
        """
        return (self.width, self.height)


@dataclass(config=PydanticConfig, eq=False)
class PaperStandard(KicadExpr):
    """
    A standard KiCad paper size.

    `KiCad paper format <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_page_settings>`_

    :param format: The paper format from the `PaperFormat` enum.
    :param orientation: The paper orientation from the `PaperOrientation` enum.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("paper").
    """

    format: Annotated[
        PaperFormat, m("kicad_no_kw", "kicad_always_quotes")
    ] = PaperFormat.A4
    orientation: Annotated[
        PaperOrientation, m("kicad_no_kw", "kicad_omits_default")
    ] = PaperOrientation.LANDSCAPE
    kicad_expr_tag_name: ClassVar[Literal["paper"]] = "paper"

    def as_dimensions_mm(self) -> tuple[float, float]:
        """
        Calculates dimensions of the paper in millimeters based on the standard.

        :returns: A tuple containing the width and height of the paper.
        """
        lookup = {
            PaperFormat.A5: (148, 210),
            PaperFormat.A4: (210, 297),
            PaperFormat.A3: (297, 420),
            PaperFormat.A2: (420, 594),
            PaperFormat.A1: (594, 841),
            PaperFormat.A0: (841, 1189),
            PaperFormat.A: (8.5 * 25.4, 11 * 25.4),
            PaperFormat.B: (11 * 25.4, 17 * 25.4),
            PaperFormat.C: (17 * 25.4, 22 * 25.4),
            PaperFormat.D: (22 * 25.4, 34 * 25.4),
            PaperFormat.E: (34 * 25.4, 44 * 25.4),
            PaperFormat.US_LETTER: (8.5 * 25.4, 11 * 25.4),
            PaperFormat.US_LEGAL: (8.5 * 25.4, 14 * 25.4),
            PaperFormat.US_LEDGER: (11 * 25.4, 17 * 25.4),
        }
        width, height = lookup[self.format]
        if self.orientation == PaperOrientation.LANDSCAPE:
            width, height = (height, width)
        return (width, height)


Paper = Union[PaperUser, PaperStandard]


@dataclass(config=PydanticConfig, eq=False)
class PolygonArc(KicadExpr):
    """
    A polygonal arc KiCad expression element.

    `KiCad arc <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_arc>`_

    :param start: The starting X-Y coordinates of the arc.
    :param mid: The midpoint X-Y coordinates of the arc.
    :param end: The ending X-Y coordinates of the arc.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("arc").
    """

    start: tuple[float, float]
    mid: tuple[float, float]
    end: tuple[float, float]

    kicad_expr_tag_name: ClassVar[Literal["arc"]] = "arc"


@dataclass(config=PydanticConfig, eq=False)
class XY(KicadExpr):
    """
    A 2D coordinate point.

    `KiCad coordinate point list <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_coordinate_point_list>`_

    :param x: The X coordinate of the point.
    :param y: The Y coordinate of the point.
    """

    x: Annotated[float, m("kicad_no_kw")]
    y: Annotated[float, m("kicad_no_kw")]


@dataclass(config=PydanticConfig, eq=False)
class Pts(KicadExpr):
    """
    A collection of points and arcs.

    `KiCad coordinate point list <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_coordinate_point_list>`_,
    `KiCad arc <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_symbol_arc>`_


    :param xys: A list of `XY` instances representing points.
    :param arcs: A list of `PolygonArc` instances representing arcs.
    """

    xys: list[XY] = field(default_factory=list)
    arcs: list[PolygonArc] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class Image(KicadExpr):
    """
    An embedded image in a KiCad expression.

    `KiCad image <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_images>`_

    :param at: The X-Y coordinates specifying the image placement.
    :param scale: The scale factor of the image.
    :param uuid: The unique identifier (UUID) for the image.
    :param data: The image data in the portable network graphics format (PNG) encoded with MIME type base64.

    """

    at: tuple[float, float]
    scale: Optional[float] = None
    uuid: UUID = field(default_factory=uuid4)
    data: list[str] = field(default_factory=list)


@dataclass(config=PydanticConfig, eq=False)
class TitleBlockComment(KicadExpr):
    """
    A comment within a KiCad title block.

    `KiCad title block <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_title_block>`_

    :param number: A sequential comment number.
    :param text: The comment text content.
    :cvar kicad_expr_tag_name: The KiCad expression tag name for this element ("comment").

    """

    number: Annotated[int, m("kicad_no_kw")] = 1
    text: Annotated[str, m("kicad_no_kw", "kicad_always_quotes")] = ""
    kicad_expr_tag_name: ClassVar[Literal["comment"]] = "comment"


@dataclass(config=PydanticConfig, eq=False)
class TitleBlock(KicadExpr):
    """
    The contents of a KiCad title block.

    `KiCad title block <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_title_block>`_


    :param title: The title of the document.
    :param date: The document date using the YYYY-MM-DD format.
    :param rev: The revision number of the document.
    :param company: The company name associated with the document.
    :param comments: The document comments where N is a number from 1 to 9 and COMMENT is a quoted string.
    """

    title: Annotated[str, m("kicad_omits_default")] = ""
    date: Annotated[str, m("kicad_omits_default")] = ""
    rev: Annotated[str, m("kicad_omits_default")] = ""
    company: Annotated[str, m("kicad_omits_default")] = ""
    comments: Annotated[list[TitleBlockComment], m("kicad_omits_default")] = field(
        default_factory=list,
    )


@dataclass(config=PydanticConfig, eq=False)
class Font(KicadExpr):
    """
    The font style for KiCad expressions.

    `KiCad text effects <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_text_effects>`_


    :param face: The font face name. Defaults to None.
    :param size: The font size (width, height) in KiCad units. Defaults to (1.27, 1.27).
    :param thickness: The font thickness.
    :param bold: Whether the font is bold or not.
    :param italic: Whether the font is italic or not.
    :param color: The font color as a 4-tuple of integers (R, G, B, A).
    """

    face: Optional[str] = None
    size: tuple[float, float] = (1.27, 1.27)
    thickness: Annotated[Optional[float], m("kicad_omits_default")] = None
    bold: Annotated[bool, m("kicad_kw_bool")] = False
    italic: Annotated[bool, m("kicad_kw_bool")] = False
    color: Annotated[tuple[int, int, int, float], m("kicad_omits_default")] = (
        0,
        0,
        0,
        1.0,
    )


@dataclass(config=PydanticConfig, eq=False)
class Effects(KicadExpr):
    """
    The text effects for KiCad expressions.

    `KiCad text effects <https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#_text_effects>`_

    :param font: How the text is shown.
    :param justify: Text justified horizontally right or left and/or vertically top or bottom and/or mirrored.
    :param hide: Whether to hide the text element or not.
    :param href: A hyperlink reference.
    """

    font: Font = field(default_factory=Font)
    justify: Annotated[
        list[Literal["left", "right", "top", "bottom", "mirror"]],
        m("kicad_omits_default"),
    ] = field(
        default_factory=list,
    )
    hide: Annotated[bool, m("kicad_kw_bool")] = False
    href: Annotated[Optional[str], m("kicad_always_quotes")] = None


class VersionError(ValueError):
    """
    Source file was produced with an unsupported KiCad version.
    """
