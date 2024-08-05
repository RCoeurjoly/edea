from typing import Type


def get_full_seq_type(value: tuple | list) -> Type[tuple | list]:
    """
    Get the full type with type args for tuples and lists

    >>> get_full_seq_type([1, 2, 3])
    list[int]

    >>> get_full_seq_type((1, "a"))
    tuple[int, str]

    >>> get_full_seq_type([(1, 2, "a")])
    list[tuple[int, int, str]]

    """
    typ = type(value)
    if typ is tuple:
        sub_types: list[Type] = []
        for v in value:
            sub = type(v)
            if sub is tuple or sub is list:
                sub = get_full_seq_type(v)
            sub_types.append(sub)
        return tuple[tuple(sub_types)]  # type: ignore
    if typ is list:
        if len(value) == 0:
            return list
        v = value[0]
        sub = type(v)
        if sub is tuple or sub is list:
            sub = get_full_seq_type(v)
        return list[sub]
    return typ


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses
