"""Settlement date arithmetic.

Each market settles a fixed number of business days after trade date
(T+1 for US equities, T+2 for most others). Business days exclude weekends
and the market's exchange holidays.

The trade date itself is never rolled: counting always starts from the day
after the trade date, even if the trade date is a weekend or holiday.
"""

from __future__ import annotations

from datetime import date, timedelta

from ledger.markets import Market, get_market, is_business_day


class CalendarCoverageError(ValueError):
    """Raised when a settlement calculation needs a date the market's
    holiday calendar does not cover."""


def calendar_years(market: Market) -> frozenset[int]:
    """Years for which the market's holiday calendar is populated."""
    return frozenset(day.year for day in market.holidays)


def _check_covered(day: date, market: Market) -> None:
    if day.year not in calendar_years(market):
        raise CalendarCoverageError(
            f"{market.code} holiday calendar does not cover {day.isoformat()}; "
            f"covered years: {sorted(calendar_years(market))}"
        )


def add_business_days(start: date, days: int, market: Market) -> date:
    if days < 0:
        raise ValueError("days must be non-negative")
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        _check_covered(current, market)
        if not is_business_day(current, market):
            continue
        remaining -= 1
    return current


def settlement_date(trade_date: date, market_code: str) -> date:
    market = get_market(market_code)
    return add_business_days(trade_date, market.settlement_days, market)


def is_settled(trade_date: date, market_code: str, as_of: date) -> bool:
    return as_of >= settlement_date(trade_date, market_code)
