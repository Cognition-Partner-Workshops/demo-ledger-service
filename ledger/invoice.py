"""Client invoice assembly and plain-text rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from ledger.models import InvoiceLine
from ledger.money import round_money


@dataclass
class Invoice:
    invoice_id: str
    account: str
    period_start: date
    period_end: date
    tax_rate: Decimal = Decimal("0")
    lines: list[InvoiceLine] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.lines = [
            InvoiceLine(description=line.description, amount=round_money(line.amount))
            for line in self.lines
        ]

    def add_line(self, description: str, amount: Decimal) -> None:
        self.lines.append(InvoiceLine(description=description, amount=round_money(amount)))

    def subtotal(self) -> Decimal:
        return round_money(sum((line.amount for line in self.lines), Decimal("0")))

    def tax(self) -> Decimal:
        return round_money(self.subtotal() * self.tax_rate)

    def total(self) -> Decimal:
        return self.subtotal() + self.tax()


def _money(value: Decimal) -> str:
    return f"{value:,.2f}"


def render_invoice(invoice: Invoice) -> str:
    width = 48
    out = [
        f"INVOICE {invoice.invoice_id}",
        f"Account: {invoice.account}",
        f"Period:  {invoice.period_start.isoformat()} to {invoice.period_end.isoformat()}",
        "-" * width,
    ]
    for line in invoice.lines:
        amount = _money(line.amount)
        out.append(f"{line.description:<{width - len(amount) - 1}} {amount}")
    out.append("-" * width)
    for label, value in (
        ("Subtotal", invoice.subtotal()),
        (f"Tax ({invoice.tax_rate * 100:.1f}%)", invoice.tax()),
        ("Total due", invoice.total()),
    ):
        amount = _money(value)
        out.append(f"{label:<{width - len(amount) - 1}} {amount}")
    return "\n".join(out)
