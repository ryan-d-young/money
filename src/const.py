from pathlib import Path
from datetime import datetime

PROJECT_NAME = "money"

ROOT = Path(".").resolve()
PROJECT = ROOT / "src" / PROJECT_NAME
SOURCES = PROJECT / "ext"

HOME = Path("~") / f".{PROJECT_NAME}"
HOME.mkdir(exist_ok=True, parents=True)

LOGS = HOME / "logs"
LOGDIR = LOGS / datetime.now().strftime("%Y-%m-%d")
LOGDIR.mkdir(exist_ok=True, parents=True)
LOGFILE = LOGDIR / datetime.now().strftime("%H-%M-%S")
LOGFILE.touch(exist_ok=True)