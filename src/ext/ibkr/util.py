from src.util import dt


def unix_to_iso(unix: int) -> str:
    unix = int(str(unix)[:-3])
    return dt.convert(unix=unix)
