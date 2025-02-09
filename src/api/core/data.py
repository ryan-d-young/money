from typing import Any, TypedDict

from pydantic import BaseModel


class _Data(TypedDict):
    @property
    def json(self) -> dict:
        raise NotImplementedError


class Record(_Data):
    data: dict[str, Any]

    @property
    def json(self) -> dict:
        return self.data


class Object(Record):
    model: type[BaseModel]

    @property
    def json(self) -> dict:
        model_instance = self.model(**self.data)
        return model_instance.model_dump()
