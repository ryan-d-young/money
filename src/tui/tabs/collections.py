from src import api
from .common import TabPane, TableDisplay, DictSelector, RowListView

from textual import on
from textual.app import ComposeResult
from textual.widgets import Input, Button, Rule
from textual.containers import Horizontal, Vertical


class CollectionsInput(RowListView):
    ...


class ProviderSelector(DictSelector):
    ...


class Collections(TabPane):
    def __init__(self, session: api.Session, *args, **kwargs):
        super().__init__(session, title="collections", id="collections")

    def compose(self) -> ComposeResult:
        with Vertical(id="collections-container-outer"):
            yield TableDisplay(api.core.Collections, id="collections-table")
            yield Rule(id="collections-rule")
            with Vertical(id="collections-container-inner"):
                yield Horizontal(
                    Input(name="name", id="collections-form-name"),
                    ProviderSelector(name="provider", id="collections-form-provider", data=self._session.providers),
                    CollectionsInput(id="collections-form-collections", data=())
                )
                yield Vertical(
                    Horizontal(
                        Input(name="item", id="collections-form-item"),
                        Button("Add", id="collections-form-add"),
                    ),
                    Horizontal(
                        Button("Create", id="collections-form-create"),
                        Button("Delete", id="collections-form-delete")
                    )
                )

    @on(Button.Pressed, "#collections-form-create")
    def create_collection(self) -> None:
        data = [self.query_one("#collections-form-item").value]
        data.append(self.query_one("#collections-form-provider").value)
        data.append(self.query_one("#collections-form-collections").data)
        self.app.db.add(api.core.Collections(*data))
        self.query_one("#collections-table").add_row(*data)

    @on(Button.Pressed, "#collections-form-delete")
    def delete_collection(self) -> None:
        data = [self.query_one("#collections-form-item").value]
        data.append(self.query_one("#collections-form-provider").value)
        data.append(self.query_one("#collections-form-collections").data)
        self.app.db.delete(api.core.Collections(*data))
        self.query_one("#collections-table").remove_row(*data)

    @on(Button.Pressed, "#collections-form-add")
    def add_collection(self) -> None:
        ...

