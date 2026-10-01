from datetime import date
from decimal import Decimal

import pytest

from ledger.models import Side, Trade
from ledger.positions import build_positions, gross_exposure, positions_for_account


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


def test_build_positions_nets_buys_and_sells():
    trades = [
        trade("T1", Side.BUY, "100", "10.00", date(2026, 3, 2)),
        trade("T2", Side.BUY, "100", "12.00", date(2026, 3, 3)),
        trade("T3", Side.SELL, "50", "15.00", date(2026, 3, 4)),
    ]
    [position] = build_positions(trades)
    assert position.quantity == Decimal("150")
    assert position.average_cost == Decimal("11.00")
    assert position.cost_basis == Decimal("1650.00")


def test_build_positions_groups_by_account_and_symbol():
    trades = [
        trade("T1", Side.BUY, "10", "5", date(2026, 3, 2), account="A", symbol="X"),
        trade("T2", Side.BUY, "20", "5", date(2026, 3, 2), account="A", symbol="Y"),
        trade("T3", Side.BUY, "30", "5", date(2026, 3, 2), account="B", symbol="X"),
    ]
    positions = build_positions(trades)
    assert [(p.account, p.symbol, p.quantity) for p in positions] == [
        ("A", "X", Decimal("10")),
        ("A", "Y", Decimal("20")),
        ("B", "X", Decimal("30")),
    ]


def test_sell_exceeding_position_raises():
    trades = [
        trade("T1", Side.BUY, "10", "5", date(2026, 3, 2)),
        trade("T2", Side.SELL, "11", "5", date(2026, 3, 3)),
    ]
    with pytest.raises(ValueError):
        build_positions(trades)


def test_oversell_after_partial_sells_raises():
    trades = [
        trade("T1", Side.BUY, "100", "10.00", date(2026, 3, 2)),
        trade("T2", Side.SELL, "60", "11.00", date(2026, 3, 3)),
        trade("T3", Side.SELL, "30", "11.00", date(2026, 3, 4)),
        trade("T4", Side.SELL, "11", "11.00", date(2026, 3, 5)),
    ]
    with pytest.raises(ValueError, match=r"T4: sell of 11 exceeds position 10"):
        build_positions(trades)


def test_sell_with_no_holdings_raises():
    trades = [
        trade("T1", Side.BUY, "10", "5", date(2026, 3, 2), symbol="ABC"),
        trade("T2", Side.SELL, "1", "5", date(2026, 3, 3), symbol="XYZ"),
    ]
    with pytest.raises(ValueError, match=r"T2: sell of 1 exceeds position 0"):
        build_positions(trades)


def test_gross_exposure_and_account_filter():
    positions = build_positions(
        [
            trade("T1", Side.BUY, "10", "5", date(2026, 3, 2), account="A", symbol="X"),
            trade("T2", Side.BUY, "20", "5", date(2026, 3, 2), account="B", symbol="Y"),
            trade("T3", Side.BUY, "5", "5", date(2026, 3, 2), account="B", symbol="Z"),
            trade("T4", Side.SELL, "5", "5", date(2026, 3, 3), account="B", symbol="Z"),
        ]
    )
    prices = {"X": Decimal("100"), "Y": Decimal("50"), "Z": Decimal("1")}
    assert gross_exposure(positions, prices) == Decimal("2000")
    assert [p.symbol for p in positions_for_account(positions, "B")] == ["Y"]
