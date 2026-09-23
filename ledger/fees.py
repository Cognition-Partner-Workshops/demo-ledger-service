"""Fee calculations for management and performance fees."""

from __future__ import annotations

from decimal import Decimal

CENT = Decimal("0.01")
BPS = Decimal("10000")


def management_fee(notional: Decimal, bps: Decimal) -> Decimal:
    """Flat management fee on a notional, quoted in basis points."""
    if notional < 0:
        raise ValueError("notional must be non-negative")
    fee = notional * bps / BPS
    return fee.quantize(CENT)


def performance_fee(gain: Decimal, rate: Decimal, hurdle: Decimal = Decimal("0")) -> Decimal:
    """Performance fee on gains above a hurdle. Negative gains earn no fee."""
    excess = gain - hurdle
    if excess <= 0:
        return Decimal("0.00")
    return (excess * rate).quantize(CENT)


def tiered_management_fee(notional: Decimal, tiers: list[tuple[Decimal, Decimal]]) -> Decimal:
    """Marginal tiered fee.

    ``tiers`` is a list of ``(upper_bound, bps)`` sorted by upper bound; the last
    tier's upper bound may be ``None``-like by passing a very large number.
    """
    remaining = notional
    lower = Decimal("0")
    total = Decimal("0")
    for upper, bps in tiers:
        if remaining <= 0:
            break
        band = min(remaining, upper - lower)
        total += band * bps / BPS
        remaining -= band
        lower = upper
    return total.quantize(CENT)
