from typing import TypedDict, TypeVar, Union, Callable, AsyncGenerator
from functools import lru_cache
from abc import ABC, abstractmethod

from . import core, session

from sqlalchemy.orm import DeclarativeBase

TargetT = TypeVar("TargetT", bound=Union[core.Router, DeclarativeBase, int])
PlanT = TypedDict("PlanT", bound=dict[int, "Command"])


class Command(Callable, ABC):
    def __init__(self, router: core.Router):
        self.router = router

    @abstractmethod
    def __call__(self, **kwargs: core.RequestKwargs) -> core.Response:
        ...
 

class Call(Command):
    def __init__(self, router: core.Router, **bound: core.RequestKwargs):
        super().__init__(router)
        self.bound = bound

    def __call__(self, **kwargs: core.RequestKwargs) -> core.Response:
        return self.router(**self.bound, **kwargs)


class Store(Command):
    def __init__(self, router: core.Router, store: DeclarativeBase):
        super().__init__(router)
        self.store = store


class Cycle(Call):
    def __call__(self, **kwargs: core.RequestKwargs) -> core.Response:
        ...

    @abstractmethod
    def condition(self, response: core.Response, *args, **kwargs) -> bool:
        ...


class Bridge(Call):
    def __init__(self, router: core.Router, target: core.Router, **bound: core.RequestKwargs):
        super().__init__(router, **bound)
        self.target = target

    def __call__(self, **kwargs: core.RequestKwargs) -> core.Response:
        ...


class Macro(core.Router):
    def __init__(self, plan: PlanT, **kwargs: core.RequestKwargs):
        self._plan = plan
        self.kwargs = kwargs

    @lru_cache(maxsize=None)
    def plan(self, *, start: int = 0, end: int = None):
        plan_ = {
            i: self._plan[k]
            for i, k in enumerate(sorted(self._plan.keys()))
            if i >= start and (end is None or i <= end)
        }
        return plan_

    async def start(self, session: session.Session, *, start: int = 0, end: int = None) -> AsyncGenerator[core.Response, None]:
        request, response = self.kwargs, None
        for k, (cmd, target) in self.plan(start=start, end=end):
            session.logger.info(f"Executing {cmd} ({k})")
            ...
            