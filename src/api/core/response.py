from .data import Object, Record, _Data
from .request import Request
from .symbols import Attribute, Identifier, Timestamp


class Response(_Data):
    request: Request | None
    identifier: Identifier | None
    timestamp: Timestamp | None
    attribute: Attribute | None
    data: Object | Record

    def __post_init__(self):
        if not isinstance(self.data, (Object, Record)):
            raise ValueError("data must be an Object or Record")
        if not self.timestamp:
            self.timestamp = Timestamp()

    @property
    def json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "identifier": self.identifier,
            "attribute": self.attribute,
            "data": self.data.json,
        }

    def __repr__(self):
        return f"<Response({self.request})>"
