"""Settlement date arithmetic.

Each market settles a fixed number of business days after trade date
(T+1 for US equities, T+2 for most others). Business days exclude weekends
and the market's exchange holidays.

A market's holiday calendar only covers the years it lists holidays for.
Counting business days through a date outside that coverage raises
``HolidayCalendarCoverageError`` rather than treating the date as open.
"""

from __future__ import annotations

from datetime import date, timedelta

from ledger.markets import Market, get_market, is_business_day


class HolidayCalendarCoverageError(ValueError):
    def __init__(self, day: date, market: Market) -> None:
        years = sorted(covered_years(market))
        coverage = ", ".join(str(y) for y in years) if years else "no years"
        super().__init__(
            f"{market.code} holiday calendar covers {coverage}; "
            f"cannot classify {day.isoformat()} as a business day"
        )
        self.day = day
        self.market = market


def covered_years(market: Market) -> frozenset[int]:
    return frozenset(holiday.year for holiday in market.holidays)


def _check_coverage(day: date, market: Market) -> None:
    if day.year not in covered_years(market):
        raise HolidayCalendarCoverageError(day, market)


def add_business_days(start: date, days: int, market: Market) -> date:
    if days < 0:
        raise ValueError("days must be non-negative")
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        _check_coverage(current, market)
        if not is_business_day(current, market):
            continue
        remaining -= 1
    return current


def settlement_date(trade_date: date, market_code: str) -> date:
    market = get_market(market_code)
    return add_business_days(trade_date, market.settlement_days, market)


def is_settled(trade_date: date, market_code: str, as_of: date) -> bool:
    return as_of >= settlement_date(trade_date, market_code)
