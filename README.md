# demo-ledger-service

A small, deliberately boring fund ledger library: settlement dates, fee
calculation, client invoices, day count conventions, positions and realised
P&L. Pure Python, no I/O, no framework.

> Sample repository owned by Cognition for demonstrations. It is not a
> customer system and contains no customer data.

## Running the tests

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The suite runs in well under a minute. CI (`.github/workflows/ci.yml`) runs the
same command on every push and pull request.

## Layout

| Module | What it does |
| --- | --- |
| `ledger/models.py` | `Trade`, `Lot`, `InvoiceLine` records and the `Side` enum |
| `ledger/markets.py` | Market reference data: settlement cycle and holiday calendar per exchange |
| `ledger/settlement.py` | `settlement_date(trade_date, market)`: T+N in business days |
| `ledger/fees.py` | Management, performance and tiered fees |
| `ledger/invoice.py` | Builds an `Invoice` from fee lines and renders it as plain text |
| `ledger/daycount.py` | ACT/360, ACT/365F and 30/360 day counts, year fractions, accrued interest |
| `ledger/positions.py` | Aggregates a trade blotter into per-account, per-symbol positions |
| `ledger/pnl.py` | Realised P&L with FIFO lot relief |

Tests live in `tests/`, one file per module. Invoice fixtures used by the
invoice tests are in `tests/fixtures/invoices.json`.

## Accounting conventions

These are the rules the library is expected to follow. When code and this
section disagree, this section is right.

### Settlement

- Settlement is T+N business days where N comes from the market
  (`settlement_days`): T+1 for XNYS, T+2 for XLON, XETR and XTKS.
- Business days exclude Saturdays, Sundays and the market's exchange holidays
  listed in `ledger/markets.py`. A trade on the day before a holiday settles
  one business day later than it otherwise would.

### Money and rounding

- All monetary amounts are `decimal.Decimal`, never floats.
- Fees and invoice amounts are rounded to the cent using **round half up**:
  a half cent always rounds away from zero (30.8625 rounds to 30.87,
  158.185 rounds to 158.19). This applies to every rounded figure that
  appears on a client invoice, including tax.

### Day counts

- `ACT/360` and `ACT/365F` use actual calendar days over 360 or 365.
- `30/360` follows the US (Bond Basis) rule: if the start date is the 31st it
  is treated as the 30th; if the end date is the 31st and the start date is
  the 30th or 31st, the end date is also treated as the 30th. So
  2026-01-31 to 2026-03-31 counts 60 days, and 2026-05-31 to 2026-08-31
  counts 90 days.

### Positions and P&L

- Positions are keyed by `(account, symbol)`. Sells reduce the position at
  its average cost; a sell larger than the open position is rejected.
- Realised P&L relieves lots first in, first out. A partial sell consumes the
  oldest lot first and leaves the remainder of the newer lot open.
- Selling more than the open lots hold raises `InsufficientPositionError`
  rather than creating a short position.

## Versioning

`ledger.__version__` is bumped on every release. Dependencies are pinned in
`requirements.txt`.
