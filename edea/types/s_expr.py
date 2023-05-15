from typing import Union


class QuotedStr(str):
    """
    A sub-class of str without any added functionality. It simply indicates
    this string should always have quotes around it when serialized.
    """


SExprList = list[Union[str, QuotedStr, "SExprList"]]
