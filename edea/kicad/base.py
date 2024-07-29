"""
Provides KicadExpr class which we use as a base for all KiCad
s-expression related dataclasses.
"""

import dataclasses
import inspect
from typing import Any, Callable, ClassVar, Type, TypeVar

from pydantic.dataclasses import dataclass

from edea._utils import to_snake_case
from edea.kicad import _equality, _parse, _serialize
from edea.kicad._fields import get_type
from edea.kicad.s_expr import SExprList

KicadExprClass = TypeVar("KicadExprClass", bound="KicadExpr")

CustomSerializerMethod = Callable[["KicadExpr", Any], list[SExprList]]
CustomSerializer = Callable[[Any], list[SExprList]]

CustomParserMethod = Callable[
    [Type["KicadExpr"], SExprList, str], tuple[Any, SExprList]
]
CustomParser = Callable[[SExprList], tuple[Any, SExprList]]


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


@dataclass
class KicadExpr:
    """
    A KiCad Expression element.

    :cvar _is_edea_kicad_expr: A class variable indicating that this class is an EDeA KiCad expression.
    """

    _is_edea_kicad_expr: ClassVar = True

    @classmethod
    @property
    def kicad_expr_tag_name(cls: Type[KicadExprClass]):
        """
        The name that KiCad uses for this in its s-expression format. By
        default this is computed from the Python class name converted to
        snake_case but it can be overridden.

        :returns: The KiCad expression tag name.
        """
        return to_snake_case(cls.__name__)

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

    def _get_custom_serializers(self) -> dict[str, CustomSerializer]:
        """
        Retrieves a dictionary of custom serializer methods associated with the class.

        :returns:  A mapping of field names to their corresponding custom serializer methods.
        """
        custom_serializers = {}
        members = inspect.getmembers(self)
        for _, method in members:
            if hasattr(method, "edea_custom_serializer_field_name"):
                custom_serializers[method.edea_custom_serializer_field_name] = method
        return custom_serializers

    @classmethod
    def _get_custom_parsers(cls) -> dict[str, CustomParser]:
        """
        Retrieves a dictionary of custom parser methods associated with the class.

        :returns: A Mapping field names to their corresponding custom parser methods.
        """
        custom_parsers = {}
        members = inspect.getmembers(cls)
        for _, method in members:
            if hasattr(method, "edea_custom_parser_field_name"):
                custom_parsers[method.edea_custom_parser_field_name] = method
        return custom_parsers

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
