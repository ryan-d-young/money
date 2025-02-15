from .router import Router
from .request import Request
from .response import Response
from .dependency import Dependency


class Command(Router): 
    ...


class Store(Command):
    ...


class Bridge(Command):
    ...


class Paginate(Command):
    ...


class Chain(Command):
    steps: dict[int, Command]
        
    def __new__(cls, *args, **kwargs):
        cls = super().__new__(cls, *args, **kwargs)
        cls._steps, ix = {}, 0
        for attr in cls.__dict__.values():
            if isinstance(attr, Command):
                cls._steps[ix], ix = attr, ix + 1
        return cls
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    async def __call__(self, request: Request, **kwargs: dict[str, Dependency]) -> Response:
        result = request
        for step in self.steps.values():
            result = await step(result, **kwargs)
        return result
    
    def __repr__(self):
        return f"<Chain({', '.join(f'{k}={v}' for k, v in self.steps.items())})>"
