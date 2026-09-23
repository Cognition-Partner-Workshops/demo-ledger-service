"""Market reference data: settlement cycles and exchange holiday calendars."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Market:
    code: str
    name: str
    settlement_days: int
    holidays: frozenset[date]
    calendar_start: date
    calendar_end: date


def _d(*ymd: tuple[int, int, int]) -> frozenset[date]:
    return frozenset(date(y, m, d) for y, m, d in ymd)


MARKETS: dict[str, Market] = {
    "XNYS": Market(
        code="XNYS",
        name="New York Stock Exchange",
        settlement_days=1,
        calendar_start=date(2026, 1, 1),
        calendar_end=date(2026, 12, 31),
        holidays=_d(
            (2026, 1, 1), (2026, 1, 19), (2026, 2, 16), (2026, 4, 3), (2026, 5, 25),
            (2026, 6, 19), (2026, 7, 3), (2026, 9, 7), (2026, 11, 26), (2026, 12, 25),
        ),
    ),
    "XLON": Market(
        code="XLON",
        name="London Stock Exchange",
        settlement_days=2,
        calendar_start=date(2026, 1, 1),
        calendar_end=date(2026, 12, 31),
        holidays=_d(
            (2026, 1, 1), (2026, 4, 3), (2026, 4, 6), (2026, 5, 4), (2026, 5, 25),
            (2026, 8, 31), (2026, 12, 25), (2026, 12, 28),
        ),
    ),
    "XETR": Market(
        code="XETR",
        name="Deutsche Boerse Xetra",
        settlement_days=2,
        calendar_start=date(2026, 1, 1),
        calendar_end=date(2026, 12, 31),
        holidays=_d(
            (2026, 1, 1), (2026, 4, 3), (2026, 4, 6), (2026, 5, 1),
            (2026, 12, 24), (2026, 12, 25), (2026, 12, 31),
        ),
    ),
    "XTKS": Market(
        code="XTKS",
        name="Tokyo Stock Exchange",
        settlement_days=2,
        calendar_start=date(2026, 1, 1),
        calendar_end=date(2026, 12, 31),
        holidays=_d(
            (2026, 1, 1), (2026, 1, 2), (2026, 1, 12), (2026, 2, 11), (2026, 2, 23),
            (2026, 3, 20), (2026, 4, 29), (2026, 5, 4), (2026, 5, 5), (2026, 5, 6),
            (2026, 7, 20), (2026, 8, 11), (2026, 9, 21), (2026, 9, 22), (2026, 9, 23),
            (2026, 10, 12), (2026, 11, 3), (2026, 11, 23), (2026, 12, 31),
        ),
    ),
}


class UnknownMarketError(KeyError):
    pass


class CalendarCoverageError(ValueError):
    pass


def get_market(code: str) -> Market:
    try:
        return MARKETS[code]
    except KeyError as exc:
        raise UnknownMarketError(code) from exc


def is_weekend(day: date) -> bool:
    return day.weekday() >= 5


def is_business_day(day: date, market: Market) -> bool:
    return not is_weekend(day) and day not in market.holidays


def assert_calendar_covers(day: date, market: Market) -> None:
    if not market.calendar_start <= day <= market.calendar_end:
        raise CalendarCoverageError(
            f"{market.code} holiday calendar covers {market.calendar_start} to "
            f"{market.calendar_end}; {day} is outside that range"
        )
