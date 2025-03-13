from uuid import UUID, uuid4


def uuid(*, string: bool = False) -> UUID | str:
    id_ = uuid4()
    if string:
        return str(id_)
    return id_
