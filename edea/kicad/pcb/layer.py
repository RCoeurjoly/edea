from typing import Literal, get_args

from edea.kicad.s_expr import QuotedStr, SExprList

CanonicalLayerName = Literal[
    "F.Cu",
    "In1.Cu",
    "In2.Cu",
    "In3.Cu",
    "In4.Cu",
    "In5.Cu",
    "In6.Cu",
    "In7.Cu",
    "In8.Cu",
    "In9.Cu",
    "In10.Cu",
    "In11.Cu",
    "In12.Cu",
    "In13.Cu",
    "In14.Cu",
    "In15.Cu",
    "In16.Cu",
    "In17.Cu",
    "In18.Cu",
    "In19.Cu",
    "In20.Cu",
    "In21.Cu",
    "In22.Cu",
    "In23.Cu",
    "In24.Cu",
    "In25.Cu",
    "In26.Cu",
    "In27.Cu",
    "In28.Cu",
    "In29.Cu",
    "In30.Cu",
    "B.Cu",
    "B.Adhes",
    "F.Adhes",
    "B.Paste",
    "F.Paste",
    "B.SilkS",
    "F.SilkS",
    "B.Mask",
    "F.Mask",
    "Dwgs.User",
    "Cmts.User",
    "Eco1.User",
    "Eco2.User",
    "Edge.Cuts",
    "F.CrtYd",
    "B.CrtYd",
    "F.Fab",
    "B.Fab",
    "User.1",
    "User.2",
    "User.3",
    "User.4",
    "User.5",
    "User.6",
    "User.7",
    "User.8",
    "User.9",
    "Margin",
    "Rescue",
]

WildCardLayerName = Literal[
    "*.Adhes",
    "*.Cu",
    "*.Mask",
    "*.Paste",
    "*.SilkS",
    "F&B.Cu",
]

LayerType = Literal["jumper", "mixed", "power", "signal", "user"]

layer_names = get_args(CanonicalLayerName)
layer_types = get_args(LayerType)

Layer = (
    tuple[int, CanonicalLayerName, LayerType]
    | tuple[int, CanonicalLayerName, LayerType, str]
)


def layer_to_list(layer: Layer) -> SExprList:
    lst = [str(layer[0]), QuotedStr(layer[1]), layer[2]]
    if len(layer) > 3:
        lst.append(QuotedStr(layer[3]))  # type: ignore
    return lst
