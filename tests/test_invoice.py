import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from ledger.fees import management_fee, performance_fee
from ledger.invoice import Invoice, render_invoice
from ledger.models import InvoiceLine

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


def test_invoice_with_tax_rounds_half_up():
    fixture = load_fixture("INV-2026-0002")
    invoice = Invoice(
        invoice_id=fixture["invoice_id"],
        account=fixture["account"],
        period_start=date.fromisoformat(fixture["period_start"]),
        period_end=date.fromisoformat(fixture["period_end"]),
        tax_rate=Decimal(fixture["tax_rate"]),
    )
    mgmt, perf = fixture["lines"]
    invoice.add_line(mgmt["description"], management_fee(Decimal(mgmt["notional"]), Decimal(mgmt["bps"])))
    invoice.add_line(perf["description"], performance_fee(Decimal(perf["gain"]), Decimal(perf["rate"])))
    assert [line.amount for line in invoice.lines] == [Decimal(mgmt["amount"]), Decimal(perf["amount"])]
    assert invoice.subtotal() == Decimal(fixture["subtotal"])
    # 1265.47 * 0.125 = 158.18375 -> 158.18
    assert invoice.tax() == Decimal(fixture["tax"])
    assert invoice.total() == Decimal(fixture["total"])


def test_preloaded_lines_round_half_up_consistently():
    invoice = Invoice(
        invoice_id="INV-X",
        account="ACC-X",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        lines=[InvoiceLine("Fee", Decimal("1.005"))],
    )
    assert invoice.subtotal() == Decimal("1.01")
    lines = render_invoice(invoice).splitlines()
    assert lines[4].endswith("1.01")
    assert lines[-1].endswith("1.01")


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
