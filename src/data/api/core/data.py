from typing import ClassVar, TypeVar, Any
from uuid import uuid4, UUID

from pydantic import BaseModel

from .symbols import Identifier

ResponseDataT = TypeVar("ResponseDataT", bound=list[dict[str, Any]])
ResponseT = TypeVar("ResponseT", bound=dict[Identifier, ResponseDataT])


class _ManagedModel:
    model: ClassVar[type[BaseModel]]
    instance: BaseModel
    def __init__(self, **kwargs):
        self.instance = self.model(**kwargs)


class Request(_ManagedModel):
    _id: UUID
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = uuid4()


class Response(_ManagedModel):
    _request: Request
    def __init__(self, request_id: UUID, **kwargs):
        super().__init__(**kwargs)
        self._id = request_id

    @classmethod
    def from_request(cls, request: Request, **kwargs):
        return cls(request._id, **kwargs)
    