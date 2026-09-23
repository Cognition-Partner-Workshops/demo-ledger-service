import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ledger.invoice import Invoice, render_invoice
from ledger.models import InvoiceLine

FIXTURES = Path(__file__).parent / "fixtures" / "invoices.json"


def load_fixtures() -> list[dict]:
    return json.loads(FIXTURES.read_text())["invoices"]


def load_fixture(invoice_id: str) -> dict:
    return next(inv for inv in load_fixtures() if inv["invoice_id"] == invoice_id)


ALL_FIXTURE_IDS = [inv["invoice_id"] for inv in load_fixtures()]


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


def test_invoice_totals_match_fixture():
    fixture = load_fixture("INV-2026-0001")
    invoice = build_invoice(fixture)
    assert invoice.subtotal() == Decimal(fixture["subtotal"])
    assert invoice.tax() == Decimal(fixture["tax"])
    assert invoice.total() == Decimal(fixture["total"])


@pytest.mark.parametrize("invoice_id", ALL_FIXTURE_IDS)
def test_all_fixture_totals_round_half_up(invoice_id):
    # INV-2026-0002 has tax 1265.48 * 0.125 = 158.185, which must round to 158.19.
    fixture = load_fixture(invoice_id)
    invoice = build_invoice(fixture)
    assert invoice.subtotal() == Decimal(fixture["subtotal"])
    assert invoice.tax() == Decimal(fixture["tax"])
    assert invoice.total() == Decimal(fixture["total"])


def test_sub_cent_lines_render_and_total_consistently():
    invoice = Invoice("INV-X", "ACC-X", date(2026, 1, 1), date(2026, 3, 31))
    invoice.lines.append(InvoiceLine("A", Decimal("1.004")))
    invoice.lines.append(InvoiceLine("B", Decimal("2.005")))
    rendered = render_invoice(invoice).splitlines()
    assert rendered[4].endswith("1.00")
    assert rendered[5].endswith("2.01")
    assert invoice.subtotal() == Decimal("3.01")
    assert invoice.total() == Decimal("3.01")


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
