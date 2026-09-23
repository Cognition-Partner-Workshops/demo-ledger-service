"""Settlement date arithmetic.

Each market settles a fixed number of business days after trade date
(T+1 for US equities, T+2 for most others). Business days exclude weekends
and the market's exchange holidays.
"""

from __future__ import annotations

from datetime import date, timedelta

from ledger.markets import Market, get_market, is_business_day


def add_business_days(start: date, days: int, market: Market) -> date:
    if days < 0:
        raise ValueError("days must be non-negative")
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if is_business_day(current, market):
            remaining -= 1
    return current


def settlement_date(trade_date: date, market_code: str) -> date:
    market = get_market(market_code)
    return add_business_days(trade_date, market.settlement_days, market)


def is_settled(trade_date: date, market_code: str, as_of: date) -> bool:
    return as_of >= settlement_date(trade_date, market_code)
