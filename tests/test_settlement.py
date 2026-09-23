from datetime import date

import pytest

from ledger.markets import CalendarCoverageError, UnknownMarketError
from ledger.settlement import is_settled, settlement_date


def test_settlement_t_plus_one_us_equity():
    # Friday trade, T+1 lands on Monday.
    assert settlement_date(date(2026, 3, 6), "XNYS") == date(2026, 3, 9)


def test_settlement_t_plus_two_spans_weekend():
    # Thursday trade in London, T+2 skips Saturday and Sunday.
    assert settlement_date(date(2026, 3, 5), "XLON") == date(2026, 3, 9)


def test_settlement_skips_market_holiday():
    # Thursday 27 Aug 2026 in London. Monday 31 Aug is the Summer bank holiday,
    # so T+2 is Tuesday 1 Sep, not Monday 31 Aug.
    assert settlement_date(date(2026, 8, 27), "XLON") == date(2026, 9, 1)


def test_is_settled_on_and_after_settlement_date():
    trade = date(2026, 3, 6)
    assert not is_settled(trade, "XNYS", date(2026, 3, 8))
    assert is_settled(trade, "XNYS", date(2026, 3, 9))
    assert is_settled(trade, "XNYS", date(2026, 3, 10))


def test_unknown_market_raises():
    with pytest.raises(UnknownMarketError):
        settlement_date(date(2026, 3, 6), "XXXX")


def test_settlement_rejects_dates_outside_calendar_coverage():
    # Thursday 31 Dec 2026 in New York: T+1 would land on 1 Jan 2027, which
    # the holiday calendar does not cover.
    with pytest.raises(CalendarCoverageError):
        settlement_date(date(2026, 12, 31), "XNYS")


def test_settlement_rejects_trade_date_outside_calendar_coverage():
    with pytest.raises(CalendarCoverageError):
        settlement_date(date(2025, 12, 30), "XLON")
