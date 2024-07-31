import inspect

from hypothesis import strategies as st

from edea.kicad.is_kicad_expr import is_kicad_expr
from edea.kicad.pcb import Property as PcbProperty
from edea.kicad.schematic import (
    Property as SchProperty,
)


def list_module_kicad_expr(module):
    classes = []
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ == module.__name__ and is_kicad_expr(cls):
            classes.append(cls)
    return classes


def any_kicad_expr_from_module(module):
    classes = list_module_kicad_expr(module)

    def non_empty(x):
        if x.kicad_expr_tag_name in ["kicad_sch", "kicad_pcb"]:
            return len(x.to_list()) > 4
        return len(x.to_list()) > 0

    def no_standalone_property(x):
        """Don't generate property as a standalone object
        The parser can't differentiate between the two prooperty classes defined in pcb, and sch in isolation.
        """
        return not isinstance(x, (PcbProperty, SchProperty))

    return st.one_of(
        [
            st.from_type(cls).filter(non_empty).filter(no_standalone_property)
            for cls in classes
        ]
    )
