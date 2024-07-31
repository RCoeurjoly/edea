"""
Provides KicadExpr class which we use as a base for all KiCad
s-expression related dataclasses.
"""

import dataclasses
from typing import Any, Callable, ClassVar, Optional, Type, TypeVar

from pydantic.dataclasses import dataclass

from edea._utils import to_snake_case
from edea.kicad import _equality, _parse, _serialize
from edea.kicad._fields import get_type
from edea.kicad.s_expr import SExprList

KicadExprClass = TypeVar("KicadExprClass", bound="KicadExpr")

CustomSerializerMethod = Callable[["KicadExpr", Any], list[SExprList]]
CustomSerializer = Callable[["KicadExpr", Any], list[SExprList]]

CustomParserMethod = Callable[
    [Type["KicadExpr"], SExprList, str], tuple[Any, SExprList]
]
CustomParser = Callable[[Type[KicadExprClass], SExprList], tuple[Any, SExprList]]


def custom_serializer(field_name: str):
    """
    Creates a decorator for customizing the serialization behavior of a data model field.

    :param field_name: The name of the field in the data model that the decorator is associated with.

    :returns: A decorator function for custom serialization.
    """

    def decorator(fn) -> CustomSerializerMethod:
        fn.edea_custom_serializer_field_name = field_name
        return fn

    return decorator


def custom_parser(field_name: str):
    """
    Creates a decorator for customizing the parsing behavior of a Pydantic data model field.

    :param field_name: The name of the field in the data model that the decorator is associated with.

    :returns: The decorated function with an attached attribute for field name reference.
    """

    def decorator(fn) -> CustomParserMethod:
        fn.edea_custom_parser_field_name = field_name
        return fn

    return decorator


class CustomizationDataTransformRegistry(type):
    def __new__(cls, name: str, bases: tuple, dct: dict[str, Any]):
        custom_parsers = {}
        custom_serializers = {}
        for attr_value in dct.values():
            if isinstance(attr_value, classmethod) and hasattr(
                attr_value, "edea_custom_parser_field_name"
            ):
                custom_parsers[attr_value.edea_custom_parser_field_name] = (  # type: ignore
                    attr_value.__func__
                )
            if callable(attr_value) and hasattr(
                attr_value, "edea_custom_serializer_field_name"
            ):
                custom_serializers[attr_value.edea_custom_serializer_field_name] = (
                    attr_value
                )

        dct["_edea_custom_parsers"] = custom_parsers
        dct["_edea_custom_serializers"] = custom_serializers
        return super().__new__(cls, name, bases, dct)


@dataclass
class KicadExpr:
    """
    A KiCad Expression element.

    :cvar _is_edea_kicad_expr: A class variable indicating that this class is an EDeA KiCad expression.
    """

    kicad_expr_tag_name: ClassVar
    _is_edea_kicad_expr: ClassVar = True
    _edea_custom_parsers: ClassVar[Optional[dict[str, CustomParser]]] = None
    _edea_custom_serializers: ClassVar[Optional[dict[str, CustomSerializer]]] = None

    @classmethod
    def from_list(cls: Type[KicadExprClass], exprs: SExprList) -> KicadExprClass:
        """
        Turns an s-expression list of arguments into an EDeA dataclass. Note that
        you omit the tag name in the s-expression so e.g. for
        `(symbol "foo" (pin 1))` you would pass `["foo", ["pin", 1]]` to this method.

        :returns: An instance of the 'KicadExpr' created from the KiCad expression data.
        """
        return _parse.from_list(cls, exprs)

    def to_list(self) -> SExprList:
        """
        Turns a a KicadExpr into an s-expression list. Note that the initial
        keyword is omitted in the return of this function. It can be retrieved
        by accessing `.kicad_expr_tag_name`.

        :returns: A list representing the KiCad expression data structure generated from the object.
        """
        return _serialize.to_list(self)

    @classmethod
    def _name_for_errors(cls):
        """
        Gets a name that we can use in error messages.
        E.g.: kicad_sch (Schematic)
        """
        name = cls.kicad_expr_tag_name
        # kicad_expr_tag_name is not callable
        # pylint: disable=comparison-with-callable
        if to_snake_case(cls.__name__) != cls.kicad_expr_tag_name:
            name += f" ({cls.__name__})"
        # pylint: enable=comparison-with-callable
        return name

    @classmethod
    def check_version(cls, v: Any) -> str:
        """
        Checks the file format version. This should be implemented by subclasses to check the file format version"

        :param v: The version number to be checked.

        raises NotImplementedError: by default.
        """
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        for field in dataclasses.fields(self):
            v_self = getattr(self, field.name)
            v_other = getattr(other, field.name)
            field_type = get_type(field)
            if not _equality.fields_equal(field_type, v_self, v_other):
                return False
        return True
