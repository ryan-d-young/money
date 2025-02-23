from collections import UserList, UserString
from datetime import datetime, date, timedelta, time
from typing import Any, ClassVar, Protocol

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from src.util import dt

ILLEGAL = {",", "(", ")"}
MAP = dict()


def _reserved() -> set[str]:
    return set(MAP.keys()) | ILLEGAL


class Serializable(Protocol):
    @property
    def json(self) -> dict: ...


class _ABCSymbol(UserString, Serializable):
    discriminator: ClassVar[str] = ""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.str_schema(
            strip_whitespace=True,
            strict=True,
            coerce_numbers_to_str=True
        )

    def __new__(cls, data: str):
        if cls.discriminator in MAP:
            raise ValueError(
                f"Duplicate symbol encountered for {cls.__name__}: {MAP[cls.discriminator]} ({cls.discriminator})"
            )
        MAP[cls.discriminator] = cls
        return super().__new__(cls, data)

    def __init__(self, data: str):
        if any(char in data for char in _reserved()):
            raise ValueError(f"Invalid symbol encountered: {data}")
        super().__init__(data.removeprefix(self.discriminator))


class Symbol(_ABCSymbol):
    def __init__(self, data: str):
        super().__init__(data)

    def __repr__(self) -> str:
        return f"{self.discriminator}{self.json}"

    @property
    def json(self) -> str:
        return self.data


class Identifier(Symbol):
    discriminator: ClassVar[str] = "$"


class Router(Symbol):
    discriminator: ClassVar[str] = "*"


class Attribute(Symbol):
    discriminator: ClassVar[str] = "."


class Provider(Symbol):
    discriminator: ClassVar[str] = "?"


class Timestamp(Symbol):
    discriminator: ClassVar[str] = "^"

    def __init__(self, data: str | datetime | date | timedelta | time | None = None):
        if data is None:
            data = f"@{dt.isotoday()}"
        elif isinstance(data, str):
            data = f"@{data}"
        else:
            data = f"@{dt.convert(data)}"
        super().__init__(data)


class Collection(UserList[Symbol]):
    discriminator: ClassVar[str] = "&"

    @staticmethod
    def _ensure_single_discriminator(*symbols: _ABCSymbol) -> None:
        if len(set([symbol.discriminator for symbol in symbols])) > 1:
            raise ValueError("Multiple discriminators encountered in provided symbols")

    def __init__(self, *symbols: _ABCSymbol):
        self._ensure_single_discriminator(*symbols)
        super().__init__(symbols)

    @staticmethod
    def _concat(*symbols: _ABCSymbol) -> str:
        return ",".join([symbol.data for symbol in symbols])

    @staticmethod
    def _parse_str(symbols: str) -> list[Symbol]:
        symbols_in = symbols.split(",")
        symbols_out = []
        while symbols_in:
            symbol = symbols_in.pop()
            discriminator = None
            for cls in MAP.values():
                if symbol.startswith(cls.discriminator):
                    discriminator = cls.discriminator
                    break
            if discriminator is None:
                raise ValueError(f"Invalid symbol encountered: {symbol}")
            symbols_out.append(
                MAP[discriminator](symbol.removeprefix(discriminator))
            )
        return symbols_out

    @classmethod
    def parse_li(cls, *symbols: str):
        symbols_out = []
        for symbol in symbols:
            if symbol.startswith(Identifier.discriminator):
                symbols_out.append(Identifier(symbol))
            elif symbol.startswith(Attribute.discriminator):
                symbols_out.append(Attribute(symbol))
            elif symbol.startswith(Timestamp.discriminator):
                symbols_out.append(Timestamp(symbol))
            else:
                raise ValueError(f"Invalid symbol encountered: {symbol}")
        return cls(*symbols_out)

    @classmethod
    def parse_str(cls, symbols: str):
        symbols_li = list({symbol.strip() for symbol in symbols.split(",")})
        return cls.parse_li(*symbols_li)

    @classmethod
    def parse_strs(cls, symbols: list[str]):
        return cls.parse_str(cls._concat(*symbols))

    @property
    def obj(self) -> str:
        return self._concat(*self.data)
