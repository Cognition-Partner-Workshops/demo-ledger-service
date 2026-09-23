"""Fee calculations for management and performance fees."""

from __future__ import annotations

from decimal import ROUND_UP, Decimal

CENT = Decimal("0.01")
BPS = Decimal("10000")


def round_cents(value: Decimal) -> Decimal:
    """Round to the cent, away from zero (30.8625 -> 30.87, 158.185 -> 158.19)."""
    return value.quantize(CENT, rounding=ROUND_UP)


def management_fee(notional: Decimal, bps: Decimal) -> Decimal:
    """Flat management fee on a notional, quoted in basis points."""
    if notional < 0:
        raise ValueError("notional must be non-negative")
    return round_cents(notional * bps / BPS)


def performance_fee(gain: Decimal, rate: Decimal, hurdle: Decimal = Decimal("0")) -> Decimal:
    """Performance fee on gains above a hurdle. Negative gains earn no fee."""
    excess = gain - hurdle
    if excess <= 0:
        return Decimal("0.00")
    return round_cents(excess * rate)


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
    return round_cents(total)
