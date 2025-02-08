from time import time, strptime as _strptime
from datetime import datetime, date as _Date, time as _Time

_ISODATE = "%Y-%m-%d"
_ISOTIME = "%H:%M:%S"
_ISODATETIME = _ISODATE + "T" + _ISOTIME
_ISODATETIMETZ = _ISODATETIME + "Z"


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


def _convert_unknown_string(s: str):
    ...


def _convert_unknown_obj(obj: datetime | _Time | _Date):
    ...


def convert(
    *args, 
    dt: datetime | None = None,
    d: _Date | None = None, 
    t: _Time | None = None,
    dt_str: str | None = None,
    d_str: str | None = None,
    t_str: str | None = None     
) -> str | datetime | _Date | _Time:
    if args and not any (kwargs := (dt, d, t, dt_str, d_str, t_str)):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                converted = _convert_unknown_string(arg)
            else:
                converted = _convert_unknown_obj(arg)
    elif len(list(map(lambda x: x is not None, kwargs))) == 1:
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
        else:
            converted = _strptime(t_str, _ISOTIME)
    return converted
