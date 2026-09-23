import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ledger.fees import management_fee, performance_fee
from ledger.invoice import Invoice, render_invoice
from ledger.models import InvoiceLine

FIXTURES = Path(__file__).parent / "fixtures" / "invoices.json"


def load_fixtures() -> list[dict]:
    return json.loads(FIXTURES.read_text())["invoices"]


def load_fixture(invoice_id: str) -> dict:
    return next(inv for inv in load_fixtures() if inv["invoice_id"] == invoice_id)


def fee_for_line(line: dict):
    if "notional" in line:
        return management_fee(Decimal(line["notional"]), Decimal(line["bps"]))
    return performance_fee(Decimal(line["gain"]), Decimal(line["rate"]))


def build_invoice(fixture: dict) -> Invoice:
    invoice = Invoice(
        invoice_id=fixture["invoice_id"],
        account=fixture["account"],
        period_start=date.fromisoformat(fixture["period_start"]),
        period_end=date.fromisoformat(fixture["period_end"]),
        tax_rate=Decimal(fixture["tax_rate"]),
    )
    for line in fixture["lines"]:
        invoice.add_line(line["description"], Decimal(line["amount"]))
    return invoice


@pytest.mark.parametrize("fixture", load_fixtures(), ids=lambda f: f["invoice_id"])
def test_invoice_totals_match_fixture(fixture):
    invoice = build_invoice(fixture)
    assert invoice.subtotal() == Decimal(fixture["subtotal"])
    assert invoice.tax() == Decimal(fixture["tax"])
    assert invoice.total() == Decimal(fixture["total"])


@pytest.mark.parametrize("fixture", load_fixtures(), ids=lambda f: f["invoice_id"])
def test_fee_lines_match_fixture(fixture):
    for line in fixture["lines"]:
        assert fee_for_line(line) == Decimal(line["amount"]), line["description"]


def test_tax_rounds_to_cent():
    invoice = build_invoice(load_fixture("INV-2026-0002"))
    assert invoice.subtotal() * invoice.tax_rate == Decimal("158.18500")
    assert invoice.tax() == Decimal("158.19")
    assert invoice.total() == Decimal("1423.67")


def test_constructor_lines_are_rounded():
    invoice = Invoice(
        invoice_id="INV-X",
        account="ACC-X",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        lines=[InvoiceLine("Fee", Decimal("1.001"))],
    )
    assert invoice.lines[0].amount == Decimal("1.01")
    assert invoice.subtotal() == Decimal("1.01")
    assert render_invoice(invoice).splitlines()[4].endswith("1.01")


def test_render_invoice_layout():
    invoice = build_invoice(load_fixture("INV-2026-0001"))
    text = render_invoice(invoice)
    lines = text.splitlines()
    assert lines[0] == "INVOICE INV-2026-0001"
    assert lines[1] == "Account: ACC-1001"
    assert lines[2] == "Period:  2026-01-01 to 2026-03-31"
    assert lines[-1].startswith("Total due")
    assert lines[-1].endswith("2,812.50")
    assert all(len(line) <= 48 for line in lines)
