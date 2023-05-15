from dataclasses import Field
from typing import Literal

MetaTag = Literal[
    # KiCad doesn't have a keyword for the property. The property appears
    # simply as words. E.g. `top` becomes `Justify(vertical="top")` and
    # `bottom` becomes `Justify(vertical="bottom")` but KiCad never uses the
    # keyword `vertical`.
    "kicad_no_kw",
    # It's a keyword boolean like `hide` which we convert to `hide=True`.
    "kicad_kw_bool",
    # KiCad uses an empty expression, with the brackets, for this keyword boolen.
    # E.g. We parse`(fields_autoplaced)` as `fields_autoplaced=True`.
    "kicad_kw_bool_empty",
    # KiCad omits this property completely when it's all default values.
    "kicad_omits_default",
    # KiCad uses "yes" and "no" for this boolean
    "kicad_bool_yes_no",
]


def make_meta(*args: MetaTag):
    meta = {}
    for tag in args:
        meta[tag] = True
    return meta


def get_meta(field: Field, tag: MetaTag):
    return field.metadata.get(tag)
