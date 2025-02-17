from . import collections, home, schedule
from .common import Tabs

tabs: Tabs = [
    ("Home", home.Home),
    ("Collections", collections.Collections),
    ("Schedule", schedule.Schedule),
]