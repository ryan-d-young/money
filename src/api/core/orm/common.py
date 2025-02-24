from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy import Table
from sqlalchemy.sql import Select


@dataclass(frozen=True)
class SelectFilter:
    attr: str
    value: Any
    op: Literal["==", "!=", ">", ">=", "<", "<=", "in", "not in"]

    def filter_query(self, query: Select, table: Table) -> Select:
        match self.op:
            case "==":
                return query.where(getattr(table, self.attr) == self.value)
            case "!=":
                return query.where(getattr(table, self.attr) != self.value)
            case ">":
                return query.where(getattr(table, self.attr) > self.value)
            case ">=":
                return query.where(getattr(table, self.attr) >= self.value)
            case "<":
                return query.where(getattr(table, self.attr) < self.value)
            case "<=":
                return query.where(getattr(table, self.attr) <= self.value)
            case "in":
                return query.where(getattr(table, self.attr).in_(self.value))
            case "not in":
                return query.where(getattr(table, self.attr).notin_(self.value))
        return query


def filter_select(
    query: Select,
    table: Table,
    *filters: SelectFilter | tuple[str, Any, Literal["==", "!=", ">", ">=", "<", "<=", "in", "not in"]],
) -> Select:
    for arg in filters:
        filter_ = SelectFilter(attr=arg[0], value=arg[1], op=arg[2]) if isinstance(arg, tuple) else arg
        query = filter_.filter_query(query, table)
    return query
