from __future__ import annotations

from datetime import datetime
from typing import List

import numpy as np
import pandas as pd

from . import models

try:
    import statsmodels.api as sm
except ImportError:  # pragma: no cover - optional runtime dependency
    sm = None

try:
    from sklearn.linear_model import LinearRegression
except ImportError:  # pragma: no cover - optional runtime dependency
    LinearRegression = None


def _entries_to_df(entries, numeric_fields, sum_fields=None):
    sum_fields = set(sum_fields or [])
    rows = []
    for entry in entries:
        row = {"date": entry.local_date}
        for field in numeric_fields:
            row[field] = getattr(entry, field)
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    agg = {
        field: ("sum" if field in sum_fields else "mean")
        for field in numeric_fields
    }
    return df.groupby("date", as_index=False).agg(agg)


def build_daily_dataframe(db, user_id: int | None = None) -> pd.DataFrame:
    health_query = db.query(models.HealthEntry)
    finance_query = db.query(models.FinanceEntry)
    productivity_query = db.query(models.ProductivityEntry)
    learning_query = db.query(models.LearningEntry)

    if user_id is not None:
        health_query = health_query.filter(models.HealthEntry.user_id == user_id)
        finance_query = finance_query.filter(models.FinanceEntry.user_id == user_id)
        productivity_query = productivity_query.filter(models.ProductivityEntry.user_id == user_id)
        learning_query = learning_query.filter(models.LearningEntry.user_id == user_id)

    health_entries = health_query.all()
    finance_entries = finance_query.all()
    productivity_entries = productivity_query.all()
    learning_entries = learning_query.all()

    health_df = _entries_to_df(
        health_entries,
        ["sleep_hours", "energy_level", "weight_kg", "wellbeing"],
    )
    finance_df = _entries_to_df(
        finance_entries,
        [
            "income",
            "expense_food",
            "expense_transport",
            "expense_health",
            "expense_other",
        ],
        sum_fields=[
            "income",
            "expense_food",
            "expense_transport",
            "expense_health",
            "expense_other",
        ],
    )
    productivity_df = _entries_to_df(
        productivity_entries,
        ["deep_work_hours", "tasks_completed", "focus_level"],
        sum_fields=["deep_work_hours", "tasks_completed"],
    )
    learning_df = _entries_to_df(
        learning_entries,
        ["study_hours"],
        sum_fields=["study_hours"],
    )

    frames = [health_df, finance_df, productivity_df, learning_df]
    merged = None
    for frame in frames:
        if frame.empty:
            continue
        merged = frame if merged is None else merged.merge(frame, on="date", how="outer")

    if merged is None:
        return pd.DataFrame()

    return merged.sort_values("date").reset_index(drop=True)


def compute_correlations(
    df: pd.DataFrame,
    min_samples: int = 5,
    min_abs: float = 0.3,
    max_items: int = 12,
):
    if df.empty:
        return []

    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[0] < min_samples:
        return []

    corr = numeric.corr(numeric_only=True)
    pairs = []
    columns = list(corr.columns)
    for i, col_a in enumerate(columns):
        for col_b in columns[i + 1 :]:
            value = corr.loc[col_a, col_b]
            if pd.isna(value):
                continue
            sample_size = numeric[[col_a, col_b]].dropna().shape[0]
            if sample_size < min_samples or abs(value) < min_abs:
                continue
            pairs.append(
                {
                    "metric_a": col_a,
                    "metric_b": col_b,
                    "correlation": float(round(value, 3)),
                    "sample_size": int(sample_size),
                }
            )

    pairs.sort(key=lambda item: abs(item["correlation"]), reverse=True)
    return pairs[:max_items]


def _sleep_vs_productivity_insight(df: pd.DataFrame):
    if "sleep_hours" not in df.columns or "deep_work_hours" not in df.columns:
        return None

    filtered = df[["sleep_hours", "deep_work_hours"]].dropna()
    if len(filtered) < 6:
        return None

    low_sleep = filtered[filtered["sleep_hours"] < 6]
    high_sleep = filtered[filtered["sleep_hours"] >= 7]
    if len(low_sleep) < 3 or len(high_sleep) < 3:
        return None

    avg_low = low_sleep["deep_work_hours"].mean()
    avg_high = high_sleep["deep_work_hours"].mean()
    if avg_high <= 0:
        return None

    drop_pct = (1 - avg_low / avg_high) * 100
    if drop_pct < 15:
        return None

    return (
        f"When you sleep under 6h, deep work drops by "
        f"{drop_pct:.0f}% compared to 7h+."
    )


def _sleep_energy_trend_insight(df: pd.DataFrame):
    if "sleep_hours" not in df.columns or "energy_level" not in df.columns:
        return None

    filtered = df[["sleep_hours", "energy_level"]].dropna()
    if len(filtered) < 6:
        return None

    if sm is not None:
        x = sm.add_constant(filtered["sleep_hours"])
        model = sm.OLS(filtered["energy_level"], x).fit()
        slope = model.params.get("sleep_hours", 0)
        if slope > 0.25:
            return (
                "Energy rises with more sleep (linear trend detected). "
                f"+{slope:.2f} energy per extra hour."
            )

    if LinearRegression is not None:
        x = filtered[["sleep_hours"]]
        y = filtered["energy_level"]
        model = LinearRegression().fit(x, y)
        slope = model.coef_[0]
        if slope > 0.25:
            return (
                "Energy rises with more sleep (trend). "
                f"+{slope:.2f} energy per extra hour."
            )

    return None


def _finance_wellbeing_insight(df: pd.DataFrame):
    if "expense_food" not in df.columns or "wellbeing" not in df.columns:
        return None

    filtered = df[["expense_food", "wellbeing"]].dropna()
    if len(filtered) < 6:
        return None

    corr = filtered["expense_food"].corr(filtered["wellbeing"])
    if corr is None or np.isnan(corr):
        return None

    if corr < -0.35:
        return (
            "Food spending tends to align with lower wellbeing "
            f"(r={corr:.2f})."
        )

    return None


def generate_insights(df: pd.DataFrame) -> List[dict]:
    insights = []

    for candidate in (
        _sleep_vs_productivity_insight,
        _sleep_energy_trend_insight,
        _finance_wellbeing_insight,
    ):
        message = candidate(df)
        if message:
            insights.append({"message": message, "severity": "info"})
        if len(insights) >= 2:
            break

    if not insights and not df.empty:
        insights.append(
            {
                "message": "Keep tracking daily inputs to unlock insights.",
                "severity": "info",
            }
        )

    return insights


def insights_payload(db, user_id: int | None = None):
    df = build_daily_dataframe(db, user_id=user_id)
    return {
        "generated_at": datetime.utcnow(),
        "insights": generate_insights(df),
    }
