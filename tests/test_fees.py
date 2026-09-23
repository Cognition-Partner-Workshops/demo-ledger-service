from decimal import Decimal

import pytest

from ledger.fees import management_fee, performance_fee, tiered_management_fee


def test_management_fee_basic():
    assert management_fee(Decimal("1000000"), Decimal("25")) == Decimal("2500.00")


def test_management_fee_fractional_bps():
    assert management_fee(Decimal("250000"), Decimal("12.5")) == Decimal("312.50")


def test_management_fee_half_cent_rounds_up():
    # 54321 * 15bps = 81.4815 -> 81.48; a quarter cent is not a half cent.
    assert management_fee(Decimal("54321.00"), Decimal("15")) == Decimal("81.48")
    # 12345 * 25bps = 30.8625 -> 30.86 for the same reason.
    assert management_fee(Decimal("12345.00"), Decimal("25")) == Decimal("30.86")
    # 100 * 12.5bps = 0.125 -> 0.13 (half up), not 0.12 (banker's rounding).
    assert management_fee(Decimal("100"), Decimal("12.5")) == Decimal("0.13")


def test_management_fee_rejects_negative_notional():
    with pytest.raises(ValueError):
        management_fee(Decimal("-1"), Decimal("25"))


def test_performance_fee_above_hurdle():
    assert performance_fee(Decimal("10000"), Decimal("0.20"), hurdle=Decimal("2000")) == Decimal(
        "1600.00"
    )


def test_performance_fee_half_cent_rounds_up():
    # 6173.025 * 0.20 = 1234.605 -> 1234.61
    assert performance_fee(Decimal("6173.025"), Decimal("0.20")) == Decimal("1234.61")


def test_performance_fee_no_fee_on_loss():
    assert performance_fee(Decimal("-500"), Decimal("0.20")) == Decimal("0.00")


def test_tiered_management_fee_marginal_bands():
    tiers = [
        (Decimal("1000000"), Decimal("50")),
        (Decimal("5000000"), Decimal("35")),
        (Decimal("1000000000"), Decimal("20")),
    ]
    # 1m @ 50bps = 5000, 4m @ 35bps = 14000, 1m @ 20bps = 2000
    assert tiered_management_fee(Decimal("6000000"), tiers) == Decimal("21000.00")


def test_tiered_management_fee_half_cent_rounds_up():
    # 100 fully inside the first band at 12.5bps = 0.125 -> 0.13
    tiers = [(Decimal("1000000"), Decimal("12.5"))]
    assert tiered_management_fee(Decimal("100"), tiers) == Decimal("0.13")
