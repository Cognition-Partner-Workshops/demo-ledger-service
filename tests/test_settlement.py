from datetime import date

import pytest

from ledger.markets import UnknownMarketError
from ledger.settlement import CalendarCoverageError, is_settled, settlement_date


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


def test_settlement_skips_consecutive_holidays():
    # Thursday 2 Apr 2026 in London. Good Friday (3 Apr) and Easter Monday
    # (6 Apr) are both closed, so T+2 is Wednesday 8 Apr.
    assert settlement_date(date(2026, 4, 2), "XLON") == date(2026, 4, 8)


def test_trade_date_on_weekend_is_not_rolled():
    # Saturday trade in New York, T+1 counts forward from Saturday: Monday.
    assert settlement_date(date(2026, 3, 7), "XNYS") == date(2026, 3, 9)


def test_trade_date_on_holiday_is_not_rolled():
    # Trade dated on the London Summer bank holiday (Mon 31 Aug 2026).
    # T+2 counts forward from that date: Tue 1 Sep, Wed 2 Sep.
    assert settlement_date(date(2026, 8, 31), "XLON") == date(2026, 9, 2)


def test_settlement_outside_calendar_coverage_raises():
    # Wed 30 Dec 2026 in London: T+2 needs 1 Jan 2027, which the holiday
    # calendar does not cover, so it must fail rather than assume it is open.
    with pytest.raises(CalendarCoverageError, match="XLON.*2027-01-01"):
        settlement_date(date(2026, 12, 30), "XLON")


def test_settlement_far_outside_calendar_coverage_raises():
    with pytest.raises(CalendarCoverageError):
        settlement_date(date(2030, 6, 3), "XNYS")


def test_trade_date_before_coverage_is_fine_when_counted_dates_are_covered():
    # The trade date itself is never checked against the calendar; only the
    # days counted after it are. 31 Dec 2025 in New York, T+1 skips
    # New Year's Day and settles Fri 2 Jan 2026.
    assert settlement_date(date(2025, 12, 31), "XNYS") == date(2026, 1, 2)


def test_is_settled_outside_calendar_coverage_raises():
    with pytest.raises(CalendarCoverageError):
        is_settled(date(2027, 3, 1), "XETR", date(2027, 3, 10))
