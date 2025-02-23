import logging
from datetime import datetime

from rich.logging import RichHandler

from . import context


def get_logger(name: str, level: int = logging.INFO, write: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    printer = RichHandler()
    printer.setLevel(level)
    logger.addHandler(printer)
    logger.addFilter(logging.Filter(name))
    if write:
        fp = context.project_root() / "logs" / datetime.now().strftime("%Y-%m-%d")
        fp.mkdir(parents=True, exist_ok=True)
        f = fp / datetime.now().strftime("%H-%M-%S")
        f.touch(exist_ok=True)
        writer = logging.FileHandler(f)
        writer.setLevel(level)
        logger.addHandler(writer)
    return logger

