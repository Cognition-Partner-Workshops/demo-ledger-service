"""Realised P&L using first-in, first-out lot relief."""

from __future__ import annotations

from collections import deque
from decimal import Decimal
from typing import Iterable

from ledger.models import Lot, Side, Trade


class InsufficientPositionError(ValueError):
    """Raised when a sell would relieve more quantity than is held."""


def realized_pnl(trades: Iterable[Trade]) -> Decimal:
    """Sum realised P&L across all sells, relieving lots FIFO per (account, symbol)."""
    lots: dict[tuple[str, str], deque[Lot]] = {}
    pnl = Decimal("0")
    for trade in sorted(trades, key=lambda t: (t.trade_date, t.trade_id)):
        key = (trade.account, trade.symbol)
        book = lots.setdefault(key, deque())
        if trade.side is Side.BUY:
            book.append(Lot(quantity=trade.quantity, price=trade.price, trade_date=trade.trade_date))
            continue
        pnl += _relieve(book, trade)
    return pnl


def _relieve(book: deque[Lot], sell: Trade) -> Decimal:
    held = sum((lot.quantity for lot in book), Decimal("0"))
    if sell.quantity > held:
        raise InsufficientPositionError(
            f"{sell.trade_id}: cannot sell {sell.quantity} {sell.symbol}, only {held} held"
        )
    remaining = sell.quantity
    pnl = Decimal("0")
    while remaining > 0:
        lot = book[0]
        taken = min(lot.quantity, remaining)
        pnl += taken * (sell.price - lot.price)
        remaining -= taken
        if taken == lot.quantity:
            book.popleft()
        else:
            book[0] = Lot(quantity=lot.quantity - taken, price=lot.price, trade_date=lot.trade_date)
    return pnl


def open_lots(trades: Iterable[Trade], account: str, symbol: str) -> list[Lot]:
    """Lots still open after applying every trade for one (account, symbol)."""
    book: deque[Lot] = deque()
    for trade in sorted(trades, key=lambda t: (t.trade_date, t.trade_id)):
        if (trade.account, trade.symbol) != (account, symbol):
            continue
        if trade.side is Side.BUY:
            book.append(Lot(quantity=trade.quantity, price=trade.price, trade_date=trade.trade_date))
        else:
            _relieve(book, trade)
    return list(book)
