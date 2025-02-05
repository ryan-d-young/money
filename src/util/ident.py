from uuid import UUID, uuid4


def uuid(*, s: bool = False) -> UUID | str:
    id_ = uuid4()
    if s:
        return str(id_)
    return id_
