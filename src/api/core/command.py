from typing import TypedDict, TypeVar, Union, Callable
from functools import lru_cache
from abc import ABC, abstractmethod

from .router import Router
from .request import RequestKwargs
from .response import Response

from sqlalchemy.orm import DeclarativeBase

TargetT = TypeVar("TargetT", bound=Union[Router, DeclarativeBase, int])
PlanT = TypedDict("PlanT", bound=dict[int, "Command"])


class Command(Callable, ABC):
    def __init__(self, router: Router):
        self.router = router

    @abstractmethod
    def __call__(self, **kwargs: RequestKwargs) -> Response:
        ...
 

class Call(Command):
    def __init__(self, router: Router, **bound: RequestKwargs):
        super().__init__(router)
        self.bound = bound

    def __call__(self, **kwargs: RequestKwargs) -> Response:
        return self.router(**self.bound, **kwargs)


class Store(Command):
    def __init__(self, router: Router, store: DeclarativeBase):
        super().__init__(router)
        self.store = store


class Cycle(Call):
    def __call__(self, **kwargs: RequestKwargs) -> Response:
        response = super().__call__(**kwargs)
        while (kwargs := self.cycle(response, **kwargs)):
            response = super().__call__(**kwargs)
        return response

    @abstractmethod
    def cycle(self, response: Response, **kwargs: RequestKwargs) -> RequestKwargs | None:
        ...


class Bridge(Call):
    def __init__(self, router: Router, target: Router, **bound: RequestKwargs):
        super().__init__(router, **bound)
        self.target = target

    def __call__(self, **kwargs: RequestKwargs) -> Response:
        router_response = super().__call__(**kwargs)
        target_response = self.target(**router_response.data, **kwargs)
        return target_response


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
