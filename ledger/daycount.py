"""Day count conventions used for accruals."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum

from ledger.money import round_cents


class DayCount(str, Enum):
    ACT_360 = "ACT/360"
    ACT_365F = "ACT/365F"
    THIRTY_360 = "30/360"


def _days_30_360(start: date, end: date) -> int:
    d1 = min(start.day, 30)
    d2 = end.day
    return 360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)


def day_count(start: date, end: date, convention: DayCount) -> int:
    if end < start:
        raise ValueError("end must not be before start")
    if convention is DayCount.THIRTY_360:
        return _days_30_360(start, end)
    return (end - start).days


def year_fraction(start: date, end: date, convention: DayCount) -> Decimal:
    days = Decimal(day_count(start, end, convention))
    if convention is DayCount.ACT_365F:
        return days / Decimal(365)
    return days / Decimal(360)


def accrued_interest(
    principal: Decimal, annual_rate: Decimal, start: date, end: date, convention: DayCount
) -> Decimal:
    return round_cents(principal * annual_rate * year_fraction(start, end, convention))
