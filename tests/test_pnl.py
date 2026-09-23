from datetime import date
from decimal import Decimal

import pytest

from ledger.models import Side, Trade
from ledger.pnl import InsufficientPositionError, open_lots, realized_pnl


def trade(trade_id, side, qty, price, day, account="ACC-1001", symbol="ABC"):
    return Trade(
        trade_id=trade_id,
        account=account,
        symbol=symbol,
        side=side,
        quantity=Decimal(qty),
        price=Decimal(price),
        trade_date=day,
        market="XNYS",
    )


def test_realized_pnl_fifo_relieves_oldest_lot_first():
    trades = [
        trade("T1", Side.BUY, "100", "10.00", date(2026, 3, 2)),
        trade("T2", Side.BUY, "100", "12.00", date(2026, 3, 3)),
        trade("T3", Side.SELL, "150", "15.00", date(2026, 3, 4)),
    ]
    # 100 @ (15 - 10) + 50 @ (15 - 12) = 500 + 150
    assert realized_pnl(trades) == Decimal("650.00")


def test_realized_pnl_is_zero_with_no_sells():
    assert realized_pnl([trade("T1", Side.BUY, "100", "10.00", date(2026, 3, 2))]) == Decimal("0")


def test_realized_pnl_is_per_account_and_symbol():
    trades = [
        trade("T1", Side.BUY, "10", "10", date(2026, 3, 2), account="A"),
        trade("T2", Side.BUY, "10", "20", date(2026, 3, 2), account="B"),
        trade("T3", Side.SELL, "10", "30", date(2026, 3, 3), account="B"),
    ]
    assert realized_pnl(trades) == Decimal("100")


def test_realized_pnl_rejects_oversell():
    buys = [
        trade("T1", Side.BUY, "100", "10.00", date(2026, 3, 2)),
        trade("T2", Side.BUY, "100", "12.00", date(2026, 3, 3)),
    ]
    # Selling exactly what is held is fine and closes every lot.
    assert realized_pnl(buys + [trade("T3", Side.SELL, "200", "15.00", date(2026, 3, 4))]) == Decimal("800.00")

    # One share more than the 200 held must be rejected, not booked as a short.
    with pytest.raises(InsufficientPositionError, match="T3"):
        realized_pnl(buys + [trade("T3", Side.SELL, "201", "15.00", date(2026, 3, 4))])


def test_open_lots_after_partial_sell():
    trades = [
        trade("T1", Side.BUY, "100", "10.00", date(2026, 3, 2)),
        trade("T2", Side.BUY, "100", "12.00", date(2026, 3, 3)),
        trade("T3", Side.SELL, "150", "15.00", date(2026, 3, 4)),
    ]
    [lot] = open_lots(trades, "ACC-1001", "ABC")
    assert lot.quantity == Decimal("50")
    assert lot.price == Decimal("12.00")
