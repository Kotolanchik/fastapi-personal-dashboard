from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd


def _add(recommendations: list[dict], message: str, severity: str = "info") -> None:
    recommendations.append({"message": message, "severity": severity})


def _recommendations_from_goals(
    df: pd.DataFrame,
    goals: list[dict[str, Any]],
    recommendations: list[dict],
) -> None:
    """Add recommendations tied to user goals (target vs current)."""
    if not goals or df.empty:
        return
    for g in goals:
        sphere = g.get("sphere")
        target_value = g.get("target_value")
        target_metric = g.get("target_metric")
        title = g.get("title", "")
        if target_value is None or not target_metric:
            continue
        col = target_metric
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if len(series) < 3:
            continue
        # Weekly goals: use sum for study_hours, deep_work_hours; else mean
        if col in ("study_hours", "deep_work_hours", "tasks_completed"):
            current = float(series.sum())
        else:
            current = float(series.mean())
        if current is None:
            continue
        if current < target_value * 0.9:
            shortfall = target_value - current
            if "sleep" in title.lower() or col == "sleep_hours":
                _add(
                    recommendations,
                    f"Цель «{title}»: сейчас в среднем {current:.1f} ч. "
                    f"Добавьте ~{shortfall:.1f} ч сна в неделю.",
                    "info",
                )
            elif col == "study_hours":
                _add(
                    recommendations,
                    f"Цель «{title}»: сейчас {current:.1f} ч в неделю. "
                    f"До цели осталось ~{shortfall:.1f} ч обучения.",
                    "info",
                )
            elif col == "deep_work_hours":
                _add(
                    recommendations,
                    f"Цель «{title}»: глубокой работы {current:.1f} ч. "
                    f"Рекомендуем +{shortfall:.1f} ч в неделю.",
                    "info",
                )


def generate_recommendations(
    df: pd.DataFrame,
    goals: list[dict[str, Any]] | None = None,
) -> list[dict]:
    recommendations: list[dict] = []
    goals = goals or []

    if df.empty:
        _add(
            recommendations,
            "Добавьте первые записи (здоровье, финансы, продуктивность, обучение) — "
            "тогда появятся персональные рекомендации.",
            "info",
        )
        return recommendations

    # --- Goal‑aware ---
    _recommendations_from_goals(df, goals, recommendations)

    # --- Sleep vs energy (existing) ---
    if "sleep_hours" in df.columns and "energy_level" in df.columns:
        sample = df[["sleep_hours", "energy_level"]].dropna()
        if len(sample) >= 5:
            corr = sample["sleep_hours"].corr(sample["energy_level"])
            if corr is not None and not np.isnan(corr) and corr > 0.3:
                _add(
                    recommendations,
                    "Увеличение сна связано с ростом энергии. Попробуйте добавить +30–60 мин сна.",
                    "info",
                )

    # --- Low average sleep ---
    if "sleep_hours" in df.columns:
        avg_sleep = df["sleep_hours"].dropna().mean()
        if avg_sleep is not None and not np.isnan(avg_sleep) and avg_sleep < 6.5:
            _add(
                recommendations,
                f"Средний сон {avg_sleep:.1f} ч — ниже 6.5 ч. Рекомендуем 7–8 ч для лучшей продуктивности.",
                "warning",
            )

    # --- Deep work vs wellbeing (existing) ---
    if "deep_work_hours" in df.columns and "wellbeing" in df.columns:
        sample = df[["deep_work_hours", "wellbeing"]].dropna()
        if len(sample) >= 5:
            corr = sample["deep_work_hours"].corr(sample["wellbeing"])
            if corr is not None and not np.isnan(corr) and corr < -0.3:
                _add(
                    recommendations,
                    "Повышенная концентрация без отдыха связана с более низким самочувствием. Планируйте перерывы.",
                    "warning",
                )

    # --- Food spend vs wellbeing (existing) ---
    if "expense_food" in df.columns and "wellbeing" in df.columns:
        sample = df[["expense_food", "wellbeing"]].dropna()
        if len(sample) >= 5:
            corr = sample["expense_food"].corr(sample["wellbeing"])
            if corr is not None and not np.isnan(corr) and corr < -0.3:
                _add(
                    recommendations,
                    "Расходы на питание связаны с самочувствием. Стоит пересмотреть рацион или бюджет.",
                    "info",
                )

    # --- Study hours: encourage consistency ---
    if "study_hours" in df.columns:
        study = df["study_hours"].dropna()
        if len(study) >= 5:
            avg_study = study.mean()
            std_study = study.std()
            if (
                std_study is not None
                and not np.isnan(std_study)
                and avg_study
                and std_study > avg_study * 0.8
            ):
                _add(
                    recommendations,
                    "Часы обучения сильно колеблются по дням. Регулярные короткие сессии часто эффективнее редких длинных.",
                    "info",
                )

    # --- Focus vs deep work: high focus but low deep work ---
    if "focus_level" in df.columns and "deep_work_hours" in df.columns:
        sample = df[["focus_level", "deep_work_hours"]].dropna()
        if len(sample) >= 5:
            avg_focus = sample["focus_level"].mean()
            avg_dw = sample["deep_work_hours"].mean()
            if avg_focus >= 7 and avg_dw < 2:
                _add(
                    recommendations,
                    "Высокий уровень фокуса, но мало часов глубокой работы. Выделите 1–2 блока по 1–2 ч без отвлечений.",
                    "info",
                )

    # --- Income vs total expenses ---
    if "income" in df.columns:
        expense_cols = [c for c in df.columns if c.startswith("expense_")]
        if expense_cols:
            total_exp = df[expense_cols].sum(axis=1)
            income = df["income"]
            sample = pd.concat([income, total_exp], axis=1).dropna()
            if len(sample) >= 5:
                ratio = (sample.iloc[:, 1] / sample.iloc[:, 0].replace(0, np.nan)).mean()
                if ratio is not None and not np.isnan(ratio) and ratio > 1.0:
                    _add(
                        recommendations,
                        "Расходы в среднем превышают доходы. Рекомендуем пересмотреть бюджет или источники дохода.",
                        "warning",
                    )

    # --- Cap and fallback ---
    if len(recommendations) > 5:
        recommendations = recommendations[:5]
    if not recommendations:
        _add(
            recommendations,
            "Продолжайте регулярный трекинг — скоро появятся персональные рекомендации.",
            "info",
        )

    return recommendations


def recommendations_payload(
    df: pd.DataFrame,
    goals: list[dict[str, Any]] | None = None,
) -> dict:
    return {
        "generated_at": datetime.utcnow(),
        "recommendations": generate_recommendations(df, goals=goals),
    }
