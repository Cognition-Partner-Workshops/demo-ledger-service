"""Monetary rounding shared by fees and invoices."""

from __future__ import annotations

from decimal import ROUND_UP, Decimal

CENT = Decimal("0.01")


def round_money(value: Decimal) -> Decimal:
    """Round to the cent, away from zero (30.8625 -> 30.87, 81.4815 -> 81.49)."""
    return value.quantize(CENT, rounding=ROUND_UP)
