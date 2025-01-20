from abc import ABC
from typing import ClassVar
from collections import UserString, UserList


class Symbol(UserString, ABC):
    discriminator: ClassVar[str] = ""
    def __repr__(self):
        return f"{self.discriminator}{self.data}"


class Identifier(Symbol):
    discriminator = "$"


class Timestamp(Symbol):
    discriminator = "@"


class Attribute(Symbol):
    discriminator = "#"


class Collection(Symbol):
    discriminator = "+"
    