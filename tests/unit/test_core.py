import pytest
from datetime import datetime

from src import api


@pytest.mark.asyncio
async def test_symbols():
    identifier = api.core.Identifier("Steve")
    assert identifier.data == "Steve"
    assert identifier.discriminator == "$"
    assert identifier.obj == "Steve"

    timestamp = api.core.Timestamp("20210101")
    assert timestamp.data == timestamp.obj == "20210101"
    assert timestamp.discriminator == "@"

    attribute = api.core.Attribute("weight")
    assert attribute.data == attribute.obj == "weight"
    assert attribute.discriminator == "#"

    identifier_2 = api.core.Identifier("Michael")
    collection = api.core.Collection(identifier, identifier_2)
    assert collection.data == ["Steve", "Michael"]
    assert collection.discriminator == "+"
    assert collection.obj == "Steve,Michael"
