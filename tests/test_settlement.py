from datetime import date

import pytest

from ledger.markets import UnknownMarketError
from ledger.settlement import is_settled, settlement_date


def test_settlement_t_plus_one_us_equity():
    # Friday trade, T+1 lands on Monday.
    assert settlement_date(date(2026, 3, 6), "XNYS") == date(2026, 3, 9)


def test_settlement_t_plus_two_spans_weekend():
    # Thursday trade in London, T+2 skips Saturday and Sunday.
    assert settlement_date(date(2026, 3, 5), "XLON") == date(2026, 3, 9)


def test_settlement_t_plus_two_over_bank_holiday_weekend():
    # Thursday 27 Aug 2026 in London, T+2 skips the weekend and lands on Monday 31 Aug.
    assert settlement_date(date(2026, 8, 27), "XLON") == date(2026, 8, 31)


def test_is_settled_on_and_after_settlement_date():
    trade = date(2026, 3, 6)
    assert not is_settled(trade, "XNYS", date(2026, 3, 8))
    assert is_settled(trade, "XNYS", date(2026, 3, 9))
    assert is_settled(trade, "XNYS", date(2026, 3, 10))


def test_unknown_market_raises():
    with pytest.raises(UnknownMarketError):
        settlement_date(date(2026, 3, 6), "XXXX")
