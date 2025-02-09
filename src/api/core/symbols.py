from abc import ABC
from collections import UserList, UserString
from datetime import datetime
from typing import Any, ClassVar

from pydantic import RootModel

from src.util import dt


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

    def __repr__(self) -> str:
        return f"{self.discriminator}{self.data}"


class Identifier(_Symbol):
    discriminator: ClassVar[str] = "$"


class Timestamp(_Symbol):
    discriminator: ClassVar[str] = "@"

    def __init__(self, data: str | None = None):
        if data is None:
            data = f"@{dt.isotoday()}"
        else:
            try:
                datetime.strptime(
                    data.removeprefix(self.discriminator), dt._ISODATETIME
                )
            except ValueError:
                raise ValueError(f"Invalid timestamp format: {data}")
        super().__init__(data)

    @property
    def obj(self) -> datetime:
        return dt.convert(dt_str=self.data)


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
