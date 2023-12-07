from typing import Type, get_args

from hypothesis import strategies as st

from edea.kicad.schematic import SubSheetInstanceProject, SymbolUseInstanceProject


def configure_hypothesis():
    # use lists of max length 2 to keep the sizes of our examples in check
    def shorter_lists(list_type: Type) -> st.SearchStrategy:
        sub_type = get_args(list_type)[0]
        return st.lists(st.from_type(sub_type), max_size=2)

    st.register_type_strategy(list, shorter_lists)

    # disallow nan and infinity on floats. XXX may be better to not allow them
    # on our models i.e. throw pydantic validation errors if they do occur
    st.register_type_strategy(float, st.floats(allow_nan=False, allow_infinity=False))

    # we need to differentiate project expressions based on what is in
    # their lists, so they need to be non-empty
    def non_empty_path(x):
        if len(x.path) == 0:
            return False
        return True

    def non_empty_project(project_type: Type) -> st.SearchStrategy:
        return st.builds(project_type).filter(non_empty_path)

    st.register_type_strategy(SymbolUseInstanceProject, non_empty_project)
    st.register_type_strategy(SubSheetInstanceProject, non_empty_project)
