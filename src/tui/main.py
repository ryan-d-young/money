from typing import Iterable

from textual.app import App
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Tab,
    TabPane,
    Tabs,
    TextArea,
)
from textual.worker import Worker

from src import api, db


class Main(textual.App):
    def compose(self) -> Iterable[textual.Widget]:
        yield textual.Header(text="Hello, World!")


if __name__ == "__main__":
    Main().run()
