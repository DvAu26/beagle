import re
from typing import Pattern, Union
from abc import ABCMeta, abstractmethod
import functools


def not_null(f):
    @functools.wraps(f)
    def wrapper(self, prop, *args, **kwargs):
        if prop is None:
            return False
        else:
            return f(self, prop, *args, **kwargs)

    return wrapper


class FieldLookup(object, metaclass=ABCMeta):  # pragma: no cover
    def __init__(self, value):
        self.value = value

    @abstractmethod
    def test(self, prop) -> bool:
        pass

    def __and__(self, other) -> "FieldLookup":
        # Contains("test.exe") & Contains("fest.exe") -> And(Contains("test.exe"), Contains("fest.exe"))
        return And(self, other)

    def __or__(self, other) -> "FieldLookup":
        return Or(self, other)

    def __invert__(self) -> "FieldLookup":
        return Not(self)


class Or(FieldLookup):
    """Boolean OR, Meant to be used with other lookups:
    >>> Or(Contains("foo"), StartsWith("bar"))
    """

    def __init__(self, *args: FieldLookup):
        self.lookups = args

    def test(self, prop: str):
        for lookup in self.lookups:
            if lookup.test(prop):
                return True

        return False


class And(FieldLookup):
    """Boolean And, Meant to be used with other lookups:
    >>> And(Contains("foo"), StartsWith("bar"), EndsWith("zar"))
    """

    def __init__(self, *args: FieldLookup):
        self.lookups = args

    def test(self, prop: str):
        for lookup in self.lookups:
            if not lookup.test(prop):
                return False

        return True


class Not(FieldLookup):
    """Boolean And, Meant to be used with other lookups:
    >>> And(Contains("foo"), StartsWith("bar"), EndsWith("zar"))
    """

    def __init__(self, arg: FieldLookup):
        self.lookup = arg

    def test(self, prop: str):
        return not self.lookup.test(prop)


class Contains(FieldLookup):
    """Case sensitve contains"""

    @not_null
    def test(self, prop: str):
        return self.value in prop


class IContains(FieldLookup):
    """Case insensitve Contains"""

    @not_null
    def test(self, prop: str):
        return str(self.value).lower() in str(prop).lower()


class Exact(FieldLookup):
    """Exact match"""

    @not_null
    def test(self, prop: str):
        return self.value == prop


class IExact(FieldLookup):
    """Insensitive Exact match"""

    @not_null
    def test(self, prop: str):
        return str(self.value).lower() == str(prop).lower()


class StartsWith(FieldLookup):
    """Property begins with"""

    @not_null
    def test(self, prop: str):
        return prop.startswith(self.value)


class EndsWith(FieldLookup):
    """Property begins endswith"""

    @not_null
    def test(self, prop: str):
        return prop.endswith(self.value)


class Regex(FieldLookup):
    def __init__(self, value: Union[str, Pattern]):
        if isinstance(value, str):
            self.value: Pattern = re.compile(value)
        else:
            self.value = value

    @not_null
    def test(self, prop: str):
        return self.value.search(prop) is not None