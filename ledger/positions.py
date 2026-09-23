"""Position aggregation from trade blotters."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Mapping

from ledger.models import Side, Trade


@dataclass
class Position:
    account: str
    symbol: str
    quantity: Decimal
    cost_basis: Decimal

    @property
    def average_cost(self) -> Decimal:
        """Return cost basis per unit, or zero when the position is flat."""
        if self.quantity == 0:
            return Decimal("0")
        return self.cost_basis / self.quantity


def build_positions(trades: Iterable[Trade]) -> list[Position]:
    """Aggregate trades into per-(account, symbol) positions at average cost."""
    books: defaultdict[tuple[str, str], dict[str, Decimal]] = defaultdict(
        lambda: {"quantity": Decimal("0"), "cost": Decimal("0")}
    )
    for trade in sorted(trades, key=lambda t: (t.trade_date, t.trade_id)):
        book = books[(trade.account, trade.symbol)]
        if trade.side is Side.BUY:
            book["quantity"] += trade.quantity
            book["cost"] += trade.notional
        else:
            if trade.quantity > book["quantity"]:
                raise ValueError(
                    f"{trade.trade_id}: sell of {trade.quantity} exceeds position {book['quantity']}"
                )
            avg = book["cost"] / book["quantity"] if book["quantity"] else Decimal("0")
            book["quantity"] -= trade.quantity
            book["cost"] -= avg * trade.quantity
    return [
        Position(account=acct, symbol=sym, quantity=b["quantity"], cost_basis=b["cost"])
        for (acct, sym), b in sorted(books.items())
    ]


def gross_exposure(positions: Iterable[Position], prices: Mapping[str, Decimal]) -> Decimal:
    """Sum the absolute market value of every position at the given prices."""
    total = Decimal("0")
    for position in positions:
        total += abs(position.quantity) * prices[position.symbol]
    return total


def positions_for_account(positions: Iterable[Position], account: str) -> list[Position]:
    """Return the non-flat positions belonging to one account."""
    return [p for p in positions if p.account == account and p.quantity != 0]
