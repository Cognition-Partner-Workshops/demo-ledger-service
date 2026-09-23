"""Settlement date arithmetic.

Each market settles a fixed number of business days after trade date
(T+1 for US equities, T+2 for most others). Business days exclude weekends
and the market's exchange holidays.

The trade date itself is never rolled: counting starts on the day after the
trade date even when the trade date falls on a weekend or holiday. Every day
counted must fall within a year the market's holiday calendar covers;
otherwise the calculation raises CalendarCoverageError rather than treating
an unknown date as open.
"""

from __future__ import annotations

from datetime import date, timedelta

from ledger.markets import Market, get_market, is_business_day


class CalendarCoverageError(ValueError):
    """The market's holiday calendar has no data for a date being counted."""


def covered_years(market: Market) -> frozenset[int]:
    """Years for which the market's holiday calendar is populated."""
    return frozenset(day.year for day in market.holidays)


def _require_covered(day: date, market: Market) -> None:
    years = covered_years(market)
    if day.year not in years:
        raise CalendarCoverageError(
            f"{market.code} holiday calendar does not cover {day.isoformat()} "
            f"(covered years: {', '.join(map(str, sorted(years))) or 'none'})"
        )


def add_business_days(start: date, days: int, market: Market) -> date:
    if days < 0:
        raise ValueError("days must be non-negative")
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        _require_covered(current, market)
        if not is_business_day(current, market):
            continue
        remaining -= 1
    return current


def settlement_date(trade_date: date, market_code: str) -> date:
    market = get_market(market_code)
    return add_business_days(trade_date, market.settlement_days, market)


def is_settled(trade_date: date, market_code: str, as_of: date) -> bool:
    return as_of >= settlement_date(trade_date, market_code)
