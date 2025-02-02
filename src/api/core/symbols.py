from abc import ABC
from typing import ClassVar, Any
from datetime import datetime
from collections import UserString, UserList

from pydantic import GetCoreSchemaHandler, TypeAdapter, RootModel
from pydantic_core import CoreSchema, core_schema


class _Discriminated(ABC, UserString):
    discriminator: ClassVar[str]
    def __init__(self, data: str):
        seq = data.removeprefix(self.discriminator)
        super().__init__(seq)

    @property
    def obj(self) -> Any:
        return self


class _Symbol(_Discriminated, RootModel[str]):
    discriminator: ClassVar[str] = ""


class Identifier(_Symbol):
    discriminator: ClassVar[str] = "$"


class Timestamp(_Symbol):
    discriminator: ClassVar[str] = "@"

    def __init__(self, data: str | None = None):
        if data is None:
            data = f"@{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}"
        else:
            try:
                datetime.strptime(data.removeprefix(self.discriminator), "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError(f"Invalid timestamp format: {data}")
        super().__init__(data)

    @property
    def obj(self) -> datetime:
        parser, parsed = lambda _obj, fmt: datetime.strptime(_obj, fmt), None
        for fmt in {"%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"}:
            try:
                parsed = parser(self, fmt)
            except ValueError:
                pass
        if not parsed:
            raise ValueError(f"Unable to parse datetime string: {self}")
        return parsed
                

class Attribute(_Symbol):
    discriminator: ClassVar[str] = "#"
    

class Collection(_Discriminated, UserList[_Symbol]):
    discriminator: ClassVar[str] = "+"

    @staticmethod
    def _raise_if_heterogenous(*symbols: _Symbol) -> None:
        if len(set([symbol.discriminator for symbol in symbols])) > 1:
            raise ValueError("Multiple discriminators encountered in provided symbols")

    def __init__(self, *symbols: _Symbol):
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


def symbol(data: str) -> Timestamp | Attribute | Identifier | Collection:
    match data[0]:
        case Identifier.discriminator:
            Identifier(data)
        case Attribute.discriminator:
            Attribute(data)
        case Timestamp.discriminator:
            Timestamp(data)
        case Collection.discriminator:
            return Collection.parse_str(data)
