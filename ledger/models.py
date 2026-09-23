"""Core domain records shared across the ledger modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Trade:
    trade_id: str
    account: str
    symbol: str
    side: Side
    quantity: Decimal
    price: Decimal
    trade_date: date
    market: str

    @property
    def notional(self) -> Decimal:
        return self.quantity * self.price

    @property
    def signed_quantity(self) -> Decimal:
        return self.quantity if self.side is Side.BUY else -self.quantity


@dataclass(frozen=True)
class Lot:
    """An open tax lot: a quantity acquired at a single price on a single day."""

    quantity: Decimal
    price: Decimal
    trade_date: date


@dataclass(frozen=True)
class InvoiceLine:
    description: str
    amount: Decimal
