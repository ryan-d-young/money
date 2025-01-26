from datetime import datetime

from src.data import api
from sqlalchemy import types as t
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.sql.functions import now
from sqlalchemy.ext.hybrid import hybrid_property

from . import models, models_generated

metadata = api.core.orm.meta.metadata("ibkr")
Base = declarative_base(metadata=metadata)


class OHLC(Base):
    __tablename__ = "ohlc"
    timestamp: Mapped[datetime] = mapped_column(t.DateTime, primary_key=True)
    symbol: Mapped[str] = mapped_column(t.String, primary_key=True)
    open_: Mapped[float] = mapped_column(t.Float, nullable=True, name="open")
    high: Mapped[float] = mapped_column(t.Float, nullable=True)
    low: Mapped[float] = mapped_column(t.Float, nullable=True)
    close: Mapped[float] = mapped_column(t.Float)
    volume: Mapped[float] = mapped_column(t.Float, nullable=True)


class FXSpot(Base):
    __tablename__ = "fx"
    timestamp: Mapped[datetime] = mapped_column(t.DateTime, primary_key=True, server_default=now())
    base: Mapped[str] = mapped_column(t.String, primary_key=True)
    terms: Mapped[str] = mapped_column(t.String, primary_key=True)
    spot: Mapped[float] = mapped_column(t.Float)


class OptionStrikes(Base):
    __tablename__ = "option_strikes"
    timestamp: Mapped[datetime] = mapped_column(t.DateTime, primary_key=True, server_default=now())
    conid: Mapped[int] = mapped_column(t.Integer, primary_key=True)
    sectype: Mapped[models_generated.SecType] = mapped_column(t.Enum(models_generated.SecType), primary_key=True)
    exchange: Mapped[models_generated.Exchange] = mapped_column(t.Enum(models_generated.Exchange))
    call: Mapped[list[int]] = mapped_column(t.ARRAY(t.Integer))
    put: Mapped[list[int]] = mapped_column(t.ARRAY(t.Integer))


class FuturesChains(Base):
    __tablename__ = "futures_chains"
    timestamp: Mapped[datetime] = mapped_column(t.DateTime, primary_key=True, server_default=now())
    symbol: Mapped[str] = mapped_column(t.String, primary_key=True)
    conid: Mapped[int] = mapped_column(t.Integer, primary_key=True)
    underlying_conid: Mapped[int] = mapped_column(t.Integer)
    expiration_date: Mapped[datetime] = mapped_column(t.DateTime)
    ltd: Mapped[datetime] = mapped_column(t.DateTime)
    short_cutoff: Mapped[datetime] = mapped_column(t.DateTime)
    long_cutoff: Mapped[datetime] = mapped_column(t.DateTime)


class AccountLedger(Base):
    __tablename__ = "account_ledger"
    timestamp: Mapped[datetime] = mapped_column(t.DateTime, primary_key=True, server_default=now())
    _ledger: Mapped[models.Ledger] = mapped_column("ledger", t.JSON)

    @hybrid_property
    def ledger(self) -> models.Ledger:
        return models.Ledger(self._ledger)

    @ledger.setter
    def set_ledger(self, value: models.Ledger):
        self._ledger = value.model_dump()


class AccountSummary(Base):
    __tablename__ = "account_summary"
    timestamp: Mapped[datetime] = mapped_column(t.DateTime, primary_key=True, server_default=now())
    _summary: Mapped[models_generated.PortfolioSummary] = mapped_column(t.JSON)

    @hybrid_property
    def summary(self) -> models_generated.PortfolioSummary:
        return models_generated.PortfolioSummary(self._summary)

    @summary.setter
    def set_summary(self, value: models.PortfolioSummary):
        self._summary = value.model_dump()


class AccountPositions(Base):
    __tablename__ = "account_positions"
    timestamp: Mapped[datetime] = mapped_column(t.DateTime, primary_key=True, server_default=now())
    _position: Mapped[models_generated.IndividualPosition] = mapped_column(t.JSON)
    
    @hybrid_property
    def position(self) -> models_generated.IndividualPosition:
        return models_generated.IndividualPosition(self._summary)

    @position.setter
    def set_position(self, value: models.IndividualPosition):
        self._position = value.model_dump()
