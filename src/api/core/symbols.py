from abc import ABC, abstractmethod
from collections import UserList, UserString
from datetime import datetime, date, timedelta, time
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from src.util import dt

ILLEGAL = {","}
RESERVED = {"$", "#", "@"}


class _ABCSymbol(UserString, ABC):
    discriminator: ClassVar[str] = ""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, 
        _source_type: Any, 
        _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.str_schema(
            strip_whitespace=True,
            strict=True,
            coerce_numbers_to_str=True,
            to_lower=True
        )

    def __init__(self, data: str):
        if any(char in data for char in ILLEGAL):
            raise ValueError(f"Invalid symbol encountered: {data}")
        elif any(char in data.removeprefix(self.discriminator) for char in RESERVED):
            raise ValueError(f"Reserved symbol encountered: {data}")
        super().__init__(data.removeprefix(self.discriminator))

    def __repr__(self) -> str:
        return f"{self.discriminator}{self.data}"

    @property
    @abstractmethod
    def obj(self) -> str:
        ...


class Symbol(_ABCSymbol):
    def __init__(self, data: str):
        super().__init__(data)

    def __repr__(self) -> str:
        return f"{self.discriminator}{self.obj}"

    @property
    def obj(self) -> str:
        return self.data


class Identifier(Symbol):
    discriminator: ClassVar[str] = "$"


class Attribute(Symbol):
    discriminator: ClassVar[str] = "#"


class Timestamp(Symbol):
    discriminator: ClassVar[str] = "@"

    def __init__(self, data: str | datetime | date | timedelta | time | None = None):
        if data is None:
            data = f"@{dt.isotoday()}"
        elif isinstance(data, str):
            data = f"@{data}"
        else:
            data = f"@{dt.convert(data)}"
        super().__init__(data)


class Collection(UserList[Symbol]):
    discriminator: ClassVar[str] = "+"

    @staticmethod
    def _raise_if_heterogenous(*symbols: _ABCSymbol) -> None:
        if len(set([symbol.discriminator for symbol in symbols])) > 1:
            raise ValueError("Multiple discriminators encountered in provided symbols")

    @staticmethod
    def _concat(*symbols: _ABCSymbol) -> str:
        return ",".join([symbol.data for symbol in symbols])

    @staticmethod
    def _parse_str(symbols: str) -> list[_ABCSymbol]:
        return [_ABCSymbol(symbol.strip()) for symbol in symbols.split(",")]

    def __init__(self, *symbols: _ABCSymbol):
        self._raise_if_heterogenous(*symbols)
        super().__init__(symbols)

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
