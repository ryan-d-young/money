from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .symbols import Identifier, Timestamp, Attribute


class Object(BaseModel):
    model: BaseModel = Field(...)
    data: dict = Field(...)

    def serialize(self) -> dict:
        model_instance = self.model(**self.data)
        return model_instance.model_dump()


class Record(BaseModel):
    timestamp: Timestamp = Field(default_factory=lambda: Timestamp(f"@{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}"))
    identifier: Identifier = Field(...)
    attribute: Attribute = Field(...)
    value: Any = Field(...)
