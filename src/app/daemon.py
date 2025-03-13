import asyncio

from src import api, util

from .common.schedule import Schedule, Item


async def handle_request(
    request: api.core.Request,
    session: api.Session,
):
    ...


async def process(
    schedule: Schedule,
    session: api.Session,
    *,
    padding: float = 0.0,
):
    async def _next_schedule_item(current_schedule_item: Item):
        session.logger.info(f"Sleeping until {current_schedule_item.t}")
        await asyncio.sleep(current_schedule_item.t - util.dt.timestamp() - padding)
        await handle_request(current_schedule_item.request, session)
        session.logger.info(f"Processed request: {current_schedule_item.request}")
    try:
        while current_schedule_item := next(schedule):
            await _next_schedule_item(current_schedule_item)
    except StopIteration:
        session.logger.info("Shutting down (schedule exhausted)")
    except KeyboardInterrupt:
        session.logger.info("Shutting down (ctrl-c pressed)")
    except Exception as e:
        session.logger.error(f"Error: {e}")
        raise
    finally:
        session.logger.info("Shutting down (finally)")


async def start(schedule: Schedule, settings: util.settings.Settings, loop: asyncio.AbstractEventLoop, *, debug: bool = False):
    logger = util.log.get_logger("daemon", level=util.log.logging.INFO if debug else util.log.logging.WARNING)
    session = await api.connect(loop=loop, logger=logger)
    await process(schedule, session, padding=settings["server_daemon_padding"])
