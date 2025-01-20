import os
from pathlib import Path
from datetime import datetime

PROJECT_NAME = "money"

ROOT = Path(".").resolve()
PROJECT = ROOT / "src" / PROJECT_NAME
SOURCES = PROJECT / "ext"

HOME = Path("~") / f".{PROJECT_NAME}"
HOME.mkdir(exist_ok=True)

LOGS = HOME / "logs"
LOGS.mkdir(exist_ok=True)
LOGS_TODAY = LOGS / datetime.today().strftime("%Y%m%d")
LOGS_TODAY.mkdir(exist_ok=True)
LOGS_TODAY_MAIN = LOGS_TODAY / ".log"
LOGS_TODAY_MAIN.touch(exist_ok=True)
