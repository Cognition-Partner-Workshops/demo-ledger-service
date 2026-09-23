import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from ledger.invoice import Invoice, render_invoice

FIXTURES = Path(__file__).parent / "fixtures" / "invoices.json"


def load_fixture(invoice_id: str) -> dict:
    data = json.loads(FIXTURES.read_text())
    return next(inv for inv in data["invoices"] if inv["invoice_id"] == invoice_id)


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
