from pathlib import Path

PROJECT_NAME = "money"

ROOT = Path(".").resolve()
PROJECT = ROOT / "src" / PROJECT_NAME
SOURCES = PROJECT / "ext"

HOME = Path("~") / f".{PROJECT_NAME}"
HOME.mkdir(exist_ok=True, parents=True)
