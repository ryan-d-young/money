from typing import Any, TypedDict

from pydantic import BaseModel


class _Data(TypedDict):
    @property
    def serialize(self) -> dict:
        raise NotImplementedError


class Record(_Data):
    data: dict[str, Any]

    def serialize(self) -> dict:
        return self.data
    

class Object(Record):
    model: type[BaseModel]

    def serialize(self) -> dict:
        model_instance = self.model(**self.data)
        return model_instance.model_dump()
