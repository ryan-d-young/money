from time import time as time_
from datetime import datetime, date, time, timedelta

_1S = timedelta(seconds=1)
_NULL_TIME = time(0, 0, 0, 0)
_EOD = time(23, 59, 59, 999999)
_ISODATE = "%Y%m%d"
_ISOTIME = "%H%M%S"
_ISODATETIME = _ISODATE + "T" + _ISOTIME
_ISODATETIMETZ = _ISODATETIME + "Z"
_ISODURATION = "P%Y%M%D"
_ISODELTA = "%H%M%S"
_ISOTIMEDELTA = _ISODURATION + "T" + _ISODELTA
ISO = {_ISODATE, _ISOTIME, _ISODATETIME, _ISODATETIMETZ, _ISODURATION, _ISOTIMEDELTA}


def timestamp() -> datetime:
    return datetime.now()


def now() -> time:
    return timestamp().time()


def utcnow() -> float:
    return time_()


def today() -> date:
    return timestamp().date()


def iso_timestamp() -> str:
    return timestamp().strftime(_ISODATETIME)


def iso_now() -> str:
    return timestamp().strftime(_ISOTIME)


def iso_today() -> str:
    return today().strftime(_ISODATE)


def elapsed(start: float) -> float:
    return utcnow() - start


def end_of_day(t: time | None = None) -> datetime:
    return datetime.combine(timestamp(), t or _EOD)


def start_of_day(t: time | None = None) -> datetime:
    return datetime.combine(timestamp(), t or _NULL_TIME)


def midnight() -> datetime:
    return timestamp().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


def schedule_time(t: time) -> float | datetime:
    return datetime.combine(timestamp(), t)


def within_duration(t1: time, t2: time, dur: timedelta = _1S) -> bool:
    return duration(t1, t2) <= dur


def duration(t1: time, t2: time) -> timedelta:
    return timedelta(
        hours=t2.hour - t1.hour,
        minutes=t2.minute - t1.minute,
        seconds=t2.second - t1.second,
        microseconds=t2.microsecond - t1.microsecond,
    )
