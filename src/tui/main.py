from typing import Iterable

from textual.app import App
from textual.worker import Worker
from textual.containers import Vertical, Horizontal, Grid, VerticalScroll
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Header, Tab, TabPane, Tabs, Footer, TextArea, Input, Button, Label

from src import api, db


class 


class Main(textual.App):
    def compose(self) -> Iterable[textual.Widget]:
        yield textual.Header(text="Hello, World!")


if __name__ == "__main__":
    Main().run()
    