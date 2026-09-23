from datetime import date

import pytest

from ledger.markets import MARKETS, UnknownMarketError
from ledger.settlement import (
    CALENDAR_YEARS,
    HolidayCalendarCoverageError,
    is_settled,
    settlement_date,
)


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
    # Thursday 24 Dec 2026 in London. Friday 25 and Monday 28 Dec are both
    # holidays, so T+2 is Wednesday 30 Dec.
    assert settlement_date(date(2026, 12, 24), "XLON") == date(2026, 12, 30)


def test_trade_dated_on_holiday_is_not_rolled():
    # Monday 31 Aug 2026 is a London holiday. Count forward from that date:
    # Tuesday 1 Sep, Wednesday 2 Sep.
    assert settlement_date(date(2026, 8, 31), "XLON") == date(2026, 9, 2)


def test_trade_dated_on_weekend_is_not_rolled():
    # Saturday 7 Mar 2026 in New York, T+1 is Monday 9 Mar.
    assert settlement_date(date(2026, 3, 7), "XNYS") == date(2026, 3, 9)


def test_trade_date_before_calendar_coverage_settles_inside_it():
    # Only the days counted need calendar coverage, not the trade date itself.
    # 1 Jan 2026 is an NYSE holiday, so T+1 from 31 Dec 2025 is 2 Jan 2026.
    assert settlement_date(date(2025, 12, 31), "XNYS") == date(2026, 1, 2)


@pytest.mark.parametrize("market_code", ["XNYS", "XLON", "XETR", "XTKS"])
def test_settlement_beyond_calendar_coverage_raises(market_code):
    with pytest.raises(HolidayCalendarCoverageError):
        settlement_date(date(2026, 12, 31), market_code)


def test_settlement_beyond_calendar_coverage_error_is_descriptive():
    with pytest.raises(HolidayCalendarCoverageError, match=r"XLON.*2026.*2027-01-01"):
        settlement_date(date(2026, 12, 30), "XLON")


def test_coverage_error_is_a_value_error():
    with pytest.raises(ValueError):
        settlement_date(date(2027, 6, 1), "XLON")


@pytest.mark.parametrize("market_code", sorted(MARKETS))
def test_every_covered_year_has_holidays_for_market(market_code):
    # CALENDAR_YEARS must only name years whose schedule is actually present.
    holiday_years = {holiday.year for holiday in MARKETS[market_code].holidays}
    assert CALENDAR_YEARS <= holiday_years


def test_is_settled_beyond_calendar_coverage_raises():
    with pytest.raises(HolidayCalendarCoverageError):
        is_settled(date(2026, 12, 31), "XLON", date(2027, 1, 5))
