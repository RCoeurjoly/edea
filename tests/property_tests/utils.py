import inspect

from hypothesis import strategies as st

from edea.types.base import is_kicad_expr


def list_module_kicad_expr(module):
    classes = []
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ == module.__name__ and is_kicad_expr(cls):
            classes.append(cls)
    return classes


def any_kicad_expr_from_module(module):
    classes = list_module_kicad_expr(module)
    return st.one_of([st.from_type(cls) for cls in classes])
