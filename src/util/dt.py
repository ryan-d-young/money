from time import time, strptime as _strptime
from datetime import datetime, date as _Date, time as _Time

_ISODATE = "%Y%m%d"
_ISOTIME = "%H%M%S"
_ISODATETIME = _ISODATE + "T" + _ISOTIME
_ISODATETIMETZ = _ISODATETIME + "Z"
_ISODURATION = "P%Y%M%D"
_ISODELTA = "%H%M%S"
_ISOTIMEDELTA = _ISODURATION + "T" + _ISODELTA
ISO = {_ISODATE, _ISOTIME, _ISODATETIME, _ISODATETIMETZ, _ISODURATION, _ISOTIMEDELTA}


def now() -> _Time:
    return datetime.now().time()


def isotime() -> str:
    return now().strftime(_ISOTIME)


def isonow() -> float:
    return time()


def today() -> datetime:
    return datetime.today()


def isotoday() -> str:
    return today().strftime(_ISODATETIME)    


def date() -> _Date:
    return today().date()


def isodate() -> str:
    return date().strftime(_ISODATE)


def elapsed(start: float) -> float:
    return now() - start


def convert(
    dt: datetime | None = None,
    d: _Date | None = None, 
    t: _Time | None = None,
    dt_str: str | None = None,
    d_str: str | None = None,
    t_str: str | None = None,
    iso: str | None = None,
    unix: int | float | None = None,
) -> str | datetime | _Date | _Time:
    if not any((dt, d, t, dt_str, d_str, t_str, iso, unix)):
        raise ValueError("No arguments provided")
    if dt:
        converted = dt.strftime(_ISODATETIME)
    elif d:
        converted = d.strftime(_ISODATE)
    elif t:
        converted = t.strftime(_ISOTIME)
    elif dt_str:
        converted = datetime.strptime(dt_str, _ISODATETIME)
    elif d_str:
        converted = datetime.strptime(d_str, _ISODATE).date()
    elif t_str:
        converted = _strptime(t_str, _ISOTIME)
    elif iso:
        for fmt in ISO:
            try:
                converted = datetime.strptime(iso, fmt)
                break
            except ValueError:
                pass
    elif unix:
        converted = datetime.fromtimestamp(unix)
    return converted
