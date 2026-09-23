from datetime import date
from decimal import Decimal

import pytest

from ledger.daycount import DayCount, accrued_interest, day_count, year_fraction


def test_act_360_quarter():
    assert day_count(date(2026, 1, 15), date(2026, 4, 15), DayCount.ACT_360) == 90
    assert year_fraction(date(2026, 1, 15), date(2026, 4, 15), DayCount.ACT_360) == Decimal("0.25")


def test_act_365f_full_year():
    assert year_fraction(date(2026, 1, 1), date(2027, 1, 1), DayCount.ACT_365F) == Decimal("1")


def test_thirty_360_mid_month():
    assert day_count(date(2026, 1, 15), date(2026, 4, 15), DayCount.THIRTY_360) == 90


def test_thirty_360_start_on_31st_to_february_end():
    assert day_count(date(2026, 1, 31), date(2026, 2, 28), DayCount.THIRTY_360) == 28


def test_accrued_interest_act_360():
    # 1,000,000 at 3.6% for 90 days ACT/360 = 9,000.00
    assert accrued_interest(
        Decimal("1000000"), Decimal("0.036"), date(2026, 1, 15), date(2026, 4, 15), DayCount.ACT_360
    ) == Decimal("9000.00")


def test_end_before_start_raises():
    with pytest.raises(ValueError):
        day_count(date(2026, 4, 15), date(2026, 1, 15), DayCount.ACT_360)
