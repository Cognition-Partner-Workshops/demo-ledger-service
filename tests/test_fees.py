from decimal import Decimal

import pytest

from ledger.fees import management_fee, performance_fee, tiered_management_fee


def test_management_fee_basic():
    assert management_fee(Decimal("1000000"), Decimal("25")) == Decimal("2500.00")


def test_management_fee_fractional_bps():
    assert management_fee(Decimal("250000"), Decimal("12.5")) == Decimal("312.50")


def test_management_fee_rounds_half_up():
    # 10 * 25bps = 0.025; half a cent rounds up, not to even.
    assert management_fee(Decimal("10"), Decimal("25")) == Decimal("0.03")


def test_performance_fee_rounds_half_up():
    # 6173.025 * 0.20 = 1234.605
    assert performance_fee(Decimal("6173.025"), Decimal("0.20")) == Decimal("1234.61")


def test_tiered_management_fee_rounds_half_up():
    # 10 @ 25bps = 0.025
    assert tiered_management_fee(Decimal("10"), [(Decimal("1000000"), Decimal("25"))]) == Decimal(
        "0.03"
    )


def test_management_fee_rejects_negative_notional():
    with pytest.raises(ValueError):
        management_fee(Decimal("-1"), Decimal("25"))


def test_performance_fee_above_hurdle():
    assert performance_fee(Decimal("10000"), Decimal("0.20"), hurdle=Decimal("2000")) == Decimal(
        "1600.00"
    )


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
