from src import api


async def handle_request(request: api.core.Request, session: api.Session) -> api.core.RouterReturnType:
    router_instance = session.router(request.provider, request.router)
    stores = router_instance.info.get("stores")
    bound = session(request.provider, request.router, **request.payload)
    router = bound()
    async for response in router:
        if stores is not None:
            await session.store(response, stores)
        yield response
