from abc import ABC, abstractmethod
from functools import lru_cache
from typing import TypeVar, Callable

from sqlalchemy.orm import DeclarativeBase

from .request import RequestKwargs
from .response import Response, ResponseFactory
from .router import Router
from .symbols import Symbol

StepT = TypeVar("StepT", bound=int)
PlanT = dict[StepT, "Factory"]
BridgeT = TypeVar("BridgeT", bound=Callable[[Router], Response])


class FactoryBase(Callable, ABC, Symbol):
    def __init__(self, target: Router):
        super().__init__()
        self.target = target

    @abstractmethod
    async def __call__(self, **kwargs: RequestKwargs) -> ResponseFactory: ...


class Factory(FactoryBase):
    discriminator = "!"

    def __init__(self, target: Router, **bound: RequestKwargs):
        super().__init__(target)
        self.bound = bound

    async def __call__(self, **kwargs: RequestKwargs) -> ResponseFactory:
        async for response in await self.target(**self.bound, **kwargs):
            yield response


class Store(FactoryBase):
    discriminator = "@"

    def __init__(self, target: Router, store: DeclarativeBase):
        super().__init__(target)
        self.store = store

    async def __call__(self, **kwargs: RequestKwargs) -> Response:
        ...


class Cycle(Factory):
    discriminator = "#"

    async def __call__(self, **kwargs: RequestKwargs) -> ResponseFactory:
        responses = [resp async for resp in super().__call__(**kwargs)]
        while kwargs := self.cycle(responses, **kwargs):
            responses = [resp async for resp in super().__call__(**kwargs)]
        for response in responses:
            yield response

    @abstractmethod
    def cycle(
        self, responses: list[Response], **kwargs: RequestKwargs
    ) -> RequestKwargs | None: ...


class Bridge(Factory):
    discriminator = "+"

    def __init__(self, target: Router, bridge: BridgeT, **bound: RequestKwargs):
        super().__init__(target, **bound)
        self.bridge = bridge

    def __call__(self, **kwargs: RequestKwargs) -> Response:
        router_response = super().__call__(**kwargs)
        router_response_transformed = self.bridge(router_response)
        return router_response_transformed


class Macro(Router):
    def __init__(self, plan: PlanT, **kwargs: RequestKwargs):
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
