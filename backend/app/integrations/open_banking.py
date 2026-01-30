"""Open Banking: fetch transactions (mock or API), categorize, aggregate -> FinanceEntry."""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from ..models import DataSource, FinanceEntry
from .base import IntegrationProvider, SyncResult


# Mock transaction categories -> FinanceEntry fields
CATEGORY_MAP = {
    "food": "expense_food",
    "groceries": "expense_food",
    "restaurant": "expense_food",
    "transport": "expense_transport",
    "fuel": "expense_transport",
    "health": "expense_health",
    "pharmacy": "expense_health",
    "income": "income",
}


def _fetch_mock_transactions(days: int = 30) -> list[dict]:
    """Return mock transactions for demo (replace with real API)."""
    from random import choice, randint
    txs = []
    today = date.today()
    categories = list(CATEGORY_MAP.keys())
    for i in range(min(days * 3, 60)):
        d = today - timedelta(days=randint(0, days))
        cat = choice(categories)
        if cat == "income":
            amount = randint(500, 3000)
        else:
            amount = -randint(5, 150)
        txs.append({"date": d.isoformat(), "amount": amount, "category": cat})
    return txs


def _aggregate_to_finance(
    transactions: list[dict],
) -> dict[date, dict[str, float]]:
    """Aggregate transactions by date into income/expense_food/transport/health/other."""
    by_date: dict[date, dict[str, float]] = {}
    for tx in transactions:
        try:
            local_date = date.fromisoformat(tx["date"])
        except (TypeError, ValueError):
            continue
        amount = float(tx.get("amount", 0))
        cat = (tx.get("category") or "other").lower()
        field = CATEGORY_MAP.get(cat, "expense_other")
        if local_date not in by_date:
            by_date[local_date] = {
                "income": 0.0,
                "expense_food": 0.0,
                "expense_transport": 0.0,
                "expense_health": 0.0,
                "expense_other": 0.0,
            }
        if field == "income":
            by_date[local_date]["income"] += max(0, amount)
        else:
            by_date[local_date][field] += abs(min(0, amount)) if amount < 0 else amount
    return by_date


def _settings_include_finance(source: Optional[DataSource], category: str) -> bool:
    if not source:
        return True
    settings = getattr(source, "sync_settings", None) or {}
    finance = settings.get("finance")
    if finance is None:
        return True
    if isinstance(finance, list) and "*" in finance:
        return True
    return isinstance(finance, list) and category in finance


class OpenBankingProvider(IntegrationProvider):
    provider = "open_banking"

    def is_configured(self, source: DataSource) -> bool:
        return bool(source.access_token or source.refresh_token or getattr(source, "metadata_json", None))

    def fetch(self, source: DataSource, db=None, settings=None) -> SyncResult:
        from sqlalchemy.orm import Session

        if not db:
            return SyncResult(status="failed", message="No database session", stats={})
        session: Session = db
        # In production: use source.access_token to call bank API and get transactions
        transactions = _fetch_mock_transactions(30)
        if not transactions:
            return SyncResult(status="success", message="No transactions", stats={"imported_records": 0})
        by_date = _aggregate_to_finance(transactions)
        tz_name = "UTC"
        imported = 0
        for local_date, amounts in by_date.items():
            income = amounts.get("income", 0) or 0
            exp_food = amounts.get("expense_food", 0) or 0
            exp_transport = amounts.get("expense_transport", 0) or 0
            exp_health = amounts.get("expense_health", 0) or 0
            exp_other = amounts.get("expense_other", 0) or 0
            if not _settings_include_finance(source, "transactions"):
                continue
            existing = (
                session.query(FinanceEntry)
                .filter(
                    FinanceEntry.user_id == source.user_id,
                    FinanceEntry.local_date == local_date,
                )
                .first()
            )
            midnight_utc = datetime(local_date.year, local_date.month, local_date.day, tzinfo=timezone.utc)
            if existing:
                existing.income = (existing.income or 0) + income
                existing.expense_food = (existing.expense_food or 0) + exp_food
                existing.expense_transport = (existing.expense_transport or 0) + exp_transport
                existing.expense_health = (existing.expense_health or 0) + exp_health
                existing.expense_other = (existing.expense_other or 0) + exp_other
                imported += 1
            else:
                entry = FinanceEntry(
                    user_id=source.user_id,
                    income=income,
                    expense_food=exp_food,
                    expense_transport=exp_transport,
                    expense_health=exp_health,
                    expense_other=exp_other,
                    recorded_at=midnight_utc,
                    local_date=local_date,
                    timezone=tz_name,
                )
                session.add(entry)
                imported += 1
        session.commit()
        return SyncResult(
            status="success",
            message="OK",
            stats={"imported_records": imported, "days": len(by_date), "transactions": len(transactions)},
        )
