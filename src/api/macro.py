from enum import Enum, auto
from typing import TypedDict, TypeVar, Union
from . import core, session

from sqlalchemy.orm import DeclarativeBase

TargetT = TypeVar("TargetT", bound=Union[core.Router, DeclarativeBase, int])
PlanT = TypedDict("PlanT", bound=dict[int, tuple["Command", TargetT]])


class Command(Enum):
    CALL = auto()
    BRIDGE = auto()
    STORE = auto()
    CYCLE = auto()


class Macro(core.Router):
    def __init__(self, plan: PlanT, **kwargs: core.RequestKwargs):
        self._plan = plan
        self.kwargs = kwargs

    def plan(self, *, start: int = 0, end: int = None):
        plan_ = {
            i: self._plan[k]
            for i, k in enumerate(sorted(self._plan.keys()))
            if i >= start and (end is None or i <= end)
        }
        return plan_

    async def start(self, session: session.Session, *, start: int = 0, end: int = None) -> core.Response:
        request, response = self.kwargs, None
        for k, (cmd, target) in self.plan(start=start, end=end):
            session.logger.info(f"Executing {cmd} ({k})")
            match cmd:
                case Command.CALL:
                    response = await target(**request)
                    yield response
                case Command.BRIDGE | Command.STORE:
                    if not response:
                        raise ValueError("No response to bridge")
                    if cmd == Command.BRIDGE:
                        request = response.data
                        response = await target(**request)
                    elif cmd == Command.STORE:
                        if not target.info["stores"]:
                            raise ValueError("No store defined for target")
                        await target.info["stores"].insert(response.data)
                    yield response
                case Command.CYCLE:
                    if not isinstance(target, int):
                        raise ValueError("Cycle target must be an integer")
                    response = await self.start(session, start=target, end=k)
                    yield response
                        