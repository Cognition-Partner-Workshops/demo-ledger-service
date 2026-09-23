"""Monetary rounding shared by fees and invoices."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def round_cents(value: Decimal) -> Decimal:
    """Round to the cent, half up: a half cent always rounds away from zero."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)
