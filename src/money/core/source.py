from typing import ClassVar, Any
from collections import UserDict

from .router import Router

import pydantic


class SourceMetadata(pydantic.BaseModel):
    pass


class Source(UserDict[str, Router]):
    name: ClassVar[str | None] = None
    routers: ClassVar[list[Router]]
    metadata_cls = ClassVar[type[SourceMetadata]]
    def __init__(self, *, metadata: dict[str, Any] | None = None):
        super().__new__({
            router.name: router 
            for router in self.routers
        })
        self.name = self.name or self.__class__.__name__
        self.metadata = metadata or {}

    def __setitem__(self, key, item):
        raise NotImplementedError("Source dict is immutable")

    def __delitem__(self, key):
        raise NotImplementedError("Source dict is immutable")
    