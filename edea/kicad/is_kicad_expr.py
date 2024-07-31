from typing import Type, get_args, get_origin


def is_kicad_expr(t: Type) -> bool:
    return hasattr(t, "_is_edea_kicad_expr")


def is_kicad_expr_list(t: Type | str):
    origin = get_origin(t)
    if origin is list:
        sub_types = get_args(t)
        if is_kicad_expr(sub_types[0]):
            return True
    return False
