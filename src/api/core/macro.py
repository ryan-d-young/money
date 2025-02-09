from sqlalchemy import Table

from .router import Router
from .session import Session
from .request import Request
from .response import Response


class Command(Router):
        ...


class Store(Command):
    def __init__(self, router: Router, store: Table):
        self.router = router
        self.store = store

    async def __call__(
        self, 
        session: Session, 
        response: Response
    ) -> Response:
        db_engine = session.dependency("db_engine")
        async with db_engine.begin() as conn:
            await conn.execute(
                self.store
                .insert()
                .values(response.json)
            )
        return response


class Bridge(Command):
    def __init__(self, router: Router, bridge: Router):
        self.router = router
        self.bridge = bridge

    async def __call__(
        self, 
        session: Session, 
        response: Response
    ) -> Response:
        response = await self.router(session, response)
        response = await self.bridge(session, response)
        return response


class Paginate(Command):
    def __init__(self, router: Router, page_size: int):
        self.router = router
        self.page_size = page_size

    async def __call__(
        self, 
        session: Session, 
        response: Response
    ) -> list[Response]:
        page_id = 1
        responses = []
        while True:
            response = await self.router(session, response)
            responses.append(response)
            if len(response.json) < self.page_size:
                break
            page_id += 1
        return responses


class Macro:
    def __init__(self, *steps: Router | Command):
        self.steps = steps

    async def __call__(
        self, 
        session: Session, 
        request: Request, 
    ) -> Response:
        response = request
        for i, step in enumerate(self.steps):
            step = session.inject(step)
            session.logger.info(f"Executing step {i+1} of {len(self.steps)}")
            response = await step(session, response)
        return response
    