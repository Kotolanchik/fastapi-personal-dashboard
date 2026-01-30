from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, List

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
        [
            "sleep_hours",
            "energy_level",
            "weight_kg",
            "wellbeing",
            "steps",
            "heart_rate_avg",
            "workout_minutes",
        ],
        sum_fields=["steps", "workout_minutes"],
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


WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def best_worst_weekday(
    df: pd.DataFrame,
    metric: str,
    higher_is_better: bool = True,
    min_days_per_weekday: int = 2,
) -> dict | None:
    """Return best and worst weekday for a metric (aggregation by weekday)."""
    if metric not in df.columns or df.empty:
        return None
    series = df[["date", metric]].dropna()
    if len(series) < 7:
        return None
    series = series.copy()
    series["date"] = pd.to_datetime(series["date"])
    series["weekday"] = series["date"].dt.dayofweek  # 0=Mon, 6=Sun
    agg = series.groupby("weekday")[metric].agg(["mean", "count"])
    agg = agg[agg["count"] >= min_days_per_weekday]
    if len(agg) < 2:
        return None
    if higher_is_better:
        best_idx = agg["mean"].idxmax()
        worst_idx = agg["mean"].idxmin()
    else:
        best_idx = agg["mean"].idxmin()
        worst_idx = agg["mean"].idxmax()
    return {
        "metric": metric,
        "best_weekday": WEEKDAY_NAMES[int(best_idx)],
        "worst_weekday": WEEKDAY_NAMES[int(worst_idx)],
        "best_value": float(round(agg.loc[best_idx, "mean"], 2)),
        "worst_value": float(round(agg.loc[worst_idx, "mean"], 2)),
    }


def linear_trend(
    df: pd.DataFrame,
    metric: str,
    days: int = 30,
    min_points: int = 5,
) -> dict | None:
    """Simple linear trend over last N days: slope and direction (up/down/neutral)."""
    if metric not in df.columns or df.empty:
        return None
    series = df[["date", metric]].dropna().sort_values("date").tail(days)
    if len(series) < min_points:
        return None
    series = series.reset_index(drop=True)
    x = np.arange(len(series))
    y = series[metric].values.astype(float)
    if np.all(y == y[0]):
        return {"metric": metric, "slope": 0.0, "direction": "neutral", "days": days}
    if LinearRegression is not None:
        model = LinearRegression().fit(x.reshape(-1, 1), y)
        slope = float(model.coef_[0])
    else:
        slope = float(np.polyfit(x, y, 1)[0])
    if abs(slope) < 1e-6:
        direction = "neutral"
    else:
        direction = "up" if slope > 0 else "down"
    return {
        "metric": metric,
        "slope": round(slope, 4),
        "direction": direction,
        "days": days,
    }


def _expenses_vs_income_trend_insight(df: pd.DataFrame):
    """Expenses grow faster than income (linear trend comparison)."""
    expense_cols = [c for c in df.columns if c.startswith("expense_")]
    if not expense_cols or "income" not in df.columns:
        return None
    df = df.copy()
    df["_total_expense"] = df[expense_cols].sum(axis=1)
    sample = df[["date", "income", "_total_expense"]].dropna()
    if len(sample) < 10:
        return None
    sample = sample.sort_values("date").tail(30)
    if len(sample) < 10:
        return None
    x = np.arange(len(sample))
    inc_slope = float(np.polyfit(x, sample["income"].values, 1)[0])
    exp_slope = float(np.polyfit(x, sample["_total_expense"].values, 1)[0])
    if inc_slope <= 0 or exp_slope <= inc_slope:
        return None
    pct = (exp_slope / inc_slope - 1) * 100
    return (
        f"Expenses are growing faster than income over the last 30 days "
        f"(expenses trend ~{pct:.0f}% steeper)."
    )


def _sleep_after_weekend_insight(df: pd.DataFrame):
    """Sleep is worse after weekends (e.g. Monday vs other days)."""
    if "sleep_hours" not in df.columns or df.empty:
        return None
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["weekday"] = df["date"].dt.dayofweek
    mon = df[df["weekday"] == 0]["sleep_hours"].dropna()
    other = df[df["weekday"] != 0]["sleep_hours"].dropna()
    if len(mon) < 3 or len(other) < 10:
        return None
    mon_avg = mon.mean()
    other_avg = other.mean()
    if mon_avg >= other_avg - 0.2:
        return None
    diff = other_avg - mon_avg
    return (
        f"Sleep is worse after weekends: Monday avg {mon_avg:.1f}h vs "
        f"{other_avg:.1f}h on other days (−{diff:.1f}h)."
    )


def _focus_higher_with_sleep_insight(df: pd.DataFrame):
    """Focus is higher on days with >6h sleep."""
    if "focus_level" not in df.columns or "sleep_hours" not in df.columns:
        return None
    low = df[df["sleep_hours"] < 6][["sleep_hours", "focus_level"]].dropna()
    high = df[df["sleep_hours"] >= 6][["sleep_hours", "focus_level"]].dropna()
    if len(low) < 3 or len(high) < 3:
        return None
    f_low = low["focus_level"].mean()
    f_high = high["focus_level"].mean()
    if f_high <= f_low + 0.3:
        return None
    return (
        f"Focus is higher on days with ≥6h sleep: {f_high:.1f} vs {f_low:.1f} "
        "on days with less sleep."
    )


def generate_insights(df: pd.DataFrame) -> List[dict]:
    insights = []

    for candidate in (
        _sleep_vs_productivity_insight,
        _sleep_energy_trend_insight,
        _finance_wellbeing_insight,
        _expenses_vs_income_trend_insight,
        _sleep_after_weekend_insight,
        _focus_higher_with_sleep_insight,
    ):
        message = candidate(df)
        if message:
            insights.append({"message": message, "severity": "info"})
        if len(insights) >= 4:
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


def trend_this_month(df: pd.DataFrame) -> List[dict]:
    """Compare key metrics: this month vs previous month → direction up/down/neutral."""
    if df.empty or "date" not in df.columns:
        return []
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    today = pd.Timestamp.now().normalize()
    this_month_start = today.replace(day=1)
    prev_month_end = this_month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)
    this_df = df[(df["date"] >= this_month_start) & (df["date"] <= today)]
    prev_df = df[(df["date"] >= prev_month_start) & (df["date"] <= prev_month_end)]
    result = []
    # Sleep
    if "sleep_hours" in df.columns:
        c = this_df["sleep_hours"].dropna().mean()
        p = prev_df["sleep_hours"].dropna().mean()
        if pd.notna(c) and pd.notna(p) and p != 0:
            result.append({
                "metric": "sleep_hours",
                "label": "Sleep (avg h)",
                "value": round(float(c), 1),
                "direction": "up" if c > p else ("down" if c < p else "neutral"),
            })
    # Weight trend
    if "weight_kg" in df.columns:
        c = this_df["weight_kg"].dropna().mean()
        p = prev_df["weight_kg"].dropna().mean()
        if pd.notna(c) and pd.notna(p):
            result.append({
                "metric": "weight_kg",
                "label": "Weight (avg kg)",
                "value": round(float(c), 1),
                "direction": "down" if c < p else ("up" if c > p else "neutral"),
            })
    # Total expenses
    expense_cols = [c for c in df.columns if c.startswith("expense_")]
    if expense_cols:
        c = this_df[expense_cols].sum().sum()
        p = prev_df[expense_cols].sum().sum()
        if pd.notna(c) and pd.notna(p):
            result.append({
                "metric": "expense_total",
                "label": "Expenses (total)",
                "value": round(float(c), 0),
                "direction": "down" if c < p else ("up" if c > p else "neutral"),
            })
    # Deep work
    if "deep_work_hours" in df.columns:
        c = this_df["deep_work_hours"].dropna().sum()
        p = prev_df["deep_work_hours"].dropna().sum()
        if pd.notna(c) and pd.notna(p):
            result.append({
                "metric": "deep_work_hours",
                "label": "Deep work (total h)",
                "value": round(float(c), 1),
                "direction": "up" if c > p else ("down" if c < p else "neutral"),
            })
    # Income
    if "income" in df.columns:
        c = this_df["income"].dropna().sum()
        p = prev_df["income"].dropna().sum()
        if pd.notna(c) and pd.notna(p):
            result.append({
                "metric": "income",
                "label": "Income (total)",
                "value": round(float(c), 0),
                "direction": "up" if c > p else ("down" if c < p else "neutral"),
            })
    return result


def insight_of_the_week(df: pd.DataFrame, goals: List[dict] | None = None) -> str | None:
    """Single highlighted insight: first from insights or recommendations."""
    from .ml.recommender import generate_recommendations

    insights = generate_insights(df)
    if insights:
        return insights[0].get("message")
    recs = generate_recommendations(df, goals=goals or [])
    if recs:
        return recs[0].get("message")
    return None


def weekday_and_trends_payload(df: pd.DataFrame) -> dict:
    """Best/worst weekday for sleep and productivity; linear trends 14/30 days."""
    payload: dict[str, Any] = {
        "best_worst_weekday": [],
        "trends_14": [],
        "trends_30": [],
    }
    for metric, higher in [("sleep_hours", True), ("deep_work_hours", True), ("weight_kg", False)]:
        if metric in df.columns:
            bw = best_worst_weekday(df, metric, higher_is_better=higher)
            if bw:
                payload["best_worst_weekday"].append(bw)
    for metric in ("sleep_hours", "deep_work_hours", "weight_kg"):
        if metric in df.columns:
            for d in (14, 30):
                t = linear_trend(df, metric, days=d)
                if t:
                    payload[f"trends_{d}"].append(t)
    expense_cols = [c for c in df.columns if c.startswith("expense_")]
    if expense_cols:
        df_temp = df.copy()
        df_temp["total_expense"] = df_temp[expense_cols].sum(axis=1)
        for d in (14, 30):
            t = linear_trend(df_temp, "total_expense", days=d)
            if t:
                payload[f"trends_{d}"].append(t)
    if "income" in df.columns:
        for d in (14, 30):
            t = linear_trend(df, "income", days=d)
            if t:
                payload[f"trends_{d}"].append(t)
    return payload


def weekly_digest(df: pd.DataFrame, period_start: date, period_end: date) -> dict:
    """Build summary by spheres + one insight for weekly report."""
    from .ml.recommender import generate_recommendations

    summary = {}
    if not df.empty:
        if "sleep_hours" in df.columns:
            summary["health"] = {
                "sleep_avg": round(float(df["sleep_hours"].mean()), 1),
                "energy_avg": round(float(df["energy_level"].mean()), 1) if "energy_level" in df.columns else None,
                "wellbeing_avg": round(float(df["wellbeing"].mean()), 1) if "wellbeing" in df.columns else None,
            }
        expense_cols = [c for c in df.columns if c.startswith("expense_")]
        if "income" in df.columns:
            summary["finance"] = {
                "income_total": round(float(df["income"].sum()), 0),
                "expense_total": round(float(df[expense_cols].sum().sum()), 0) if expense_cols else 0,
            }
        if "deep_work_hours" in df.columns:
            summary["productivity"] = {
                "deep_work_total": round(float(df["deep_work_hours"].sum()), 1),
                "tasks_total": int(df["tasks_completed"].sum()) if "tasks_completed" in df.columns else None,
                "focus_avg": round(float(df["focus_level"].mean()), 1) if "focus_level" in df.columns else None,
            }
        if "study_hours" in df.columns:
            summary["learning"] = {
                "study_total": round(float(df["study_hours"].sum()), 1),
            }
    insights = generate_insights(df)
    recs = generate_recommendations(df, goals=None)
    insight = None
    if insights:
        insight = insights[0].get("message")
    elif recs:
        insight = recs[0].get("message")
    return {
        "period_start": period_start,
        "period_end": period_end,
        "summary": summary,
        "insight": insight,
        "generated_at": datetime.utcnow(),
    }
