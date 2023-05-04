from typing import get_args, Type, List
from hypothesis import strategies as st


def configure_hypothesis():
    # use lists of max length 2 to keep the sizes of our examples in check
    def shorter_lists(list_type: Type) -> st.SearchStrategy:
        sub_type = get_args(list_type)[0]
        return st.lists(st.from_type(sub_type), max_size=2)

    # need to use capital L `List` here
    # https://github.com/HypothesisWorks/hypothesis/issues/3635
    st.register_type_strategy(List, shorter_lists)

    # disallow nan and infinity on floats. XXX may be better to not allow them
    # on our models i.e. throw pydantic validation errors if they do occur
    st.register_type_strategy(float, st.floats(allow_nan=False, allow_infinity=False))
