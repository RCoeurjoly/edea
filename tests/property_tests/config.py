from typing import Type, get_args

from hypothesis import strategies as st

from edea.kicad.schematic import (
    Property as SchProperty,
)
from edea.kicad.schematic import (
    Sheet,
    SubSheetInstanceProject,
    SymbolUse,
    SymbolUseInstanceProject,
)


def configure_hypothesis():
    # use lists of max length 2 to keep the sizes of our examples in check
    def shorter_lists(list_type: Type) -> st.SearchStrategy:
        sub_type = get_args(list_type)[0]
        return st.lists(st.from_type(sub_type), max_size=2)

    st.register_type_strategy(list, shorter_lists)

    # disallow nan and infinity on floats. XXX may be better to not allow them
    # on our models i.e. throw pydantic validation errors if they do occur
    st.register_type_strategy(float, st.floats(allow_nan=False, allow_infinity=False))

    st.register_type_strategy(SymbolUseInstanceProject, _non_empty_project)
    st.register_type_strategy(SubSheetInstanceProject, _non_empty_project)

    st.register_type_strategy(Sheet, _sheet_with_name_and_file)
    st.register_type_strategy(SymbolUse, _symbol_use_with_ref_and_value)


def _non_empty_project(project_type: Type) -> st.SearchStrategy:
    # we need to differentiate project expressions based on what is in
    # their lists, so they need to be non-empty
    def non_empty_paths(x):
        if len(x.paths) == 0:
            return False
        return True

    return st.builds(project_type).filter(non_empty_paths)  # type: ignore


def _sheet_with_name_and_file(sheet_type: Type[Sheet]) -> st.SearchStrategy:
    # sheets need a name and file property
    def prop_with_key(key) -> st.SearchStrategy:
        return st.builds(SchProperty, key=st.sampled_from([key]))

    def sheet_props() -> st.SearchStrategy:
        props = st.one_of(prop_with_key("Sheetname"), prop_with_key("Sheetfile"))
        return st.lists(props, min_size=2).filter(
            lambda xs: xs[0].key == "Sheetname" and xs[1].key == "Sheetfile"
        )

    return st.builds(sheet_type, properties=sheet_props())


def _symbol_use_with_ref_and_value(sheet_type: Type[SymbolUse]) -> st.SearchStrategy:
    # symbols need a reference and value property
    def prop_with_key(key) -> st.SearchStrategy:
        return st.builds(SchProperty, key=st.sampled_from([key]))

    def sheet_props() -> st.SearchStrategy:
        props = st.one_of(prop_with_key("Reference"), prop_with_key("Value"))
        return st.lists(props, min_size=2).filter(
            lambda xs: xs[0].key == "Reference" and xs[1].key == "Value"
        )

    return st.builds(sheet_type, properties=sheet_props())
