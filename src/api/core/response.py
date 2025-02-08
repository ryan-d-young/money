from .data import Object, Record, _Data
from .request import Request
from .symbols import Identifier, Timestamp, Attribute


class Response(_Data):
    request: Request
    identifier: Identifier
    timestamp: Timestamp
    attribute: Attribute
    data: Object | Record
    
    def __post_init__(self):
        if not isinstance(self.data, (Object, Record)):
            raise ValueError("data must be an Object or Record")

    def json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "identifier": self.identifier,
            "attribute": self.attribute,
            "data": self.data.json
        }
