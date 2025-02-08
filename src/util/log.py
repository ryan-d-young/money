import logging

from rich.logging import RichHandler

from src import const

LOGS = const.HOME / "logs"
LOGS.mkdir(parents=True, exist_ok=True)


def get_logger(name: str, level: int = logging.INFO, write: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    printer = RichHandler()
    printer.setLevel(level)
    logger.addHandler(printer)
    logger.addFilter(logging.Filter(name))
    if write:
        writer = logging.FileHandler(const.LOGFILE)
        writer.setLevel(level)
        logger.addHandler(writer)
    return logger

