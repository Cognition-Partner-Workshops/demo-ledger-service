from decimal import Decimal

import pytest

from ledger.fees import custody_fee, management_fee, performance_fee, tiered_management_fee


def test_management_fee_basic():
    assert management_fee(Decimal("1000000"), Decimal("25")) == Decimal("2500.00")


def test_management_fee_fractional_bps():
    assert management_fee(Decimal("250000"), Decimal("12.5")) == Decimal("312.50")


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


def test_custody_fee_above_minimum():
    # 2m @ 10bps = 2000, above the 500 minimum
    assert custody_fee(Decimal("2000000"), Decimal("10"), minimum=Decimal("500")) == Decimal(
        "2000.00"
    )


def test_custody_fee_floored_at_minimum():
    # 100k @ 10bps = 100, below the 250 minimum
    assert custody_fee(Decimal("100000"), Decimal("10"), minimum=Decimal("250")) == Decimal(
        "250.00"
    )


def test_custody_fee_no_minimum():
    assert custody_fee(Decimal("50000"), Decimal("8")) == Decimal("40.00")


def test_custody_fee_rejects_negative_notional():
    with pytest.raises(ValueError):
        custody_fee(Decimal("-1"), Decimal("10"))


def test_custody_fee_rejects_negative_minimum():
    with pytest.raises(ValueError):
        custody_fee(Decimal("1000"), Decimal("10"), minimum=Decimal("-1"))
