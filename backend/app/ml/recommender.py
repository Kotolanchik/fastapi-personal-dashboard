from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd


def generate_recommendations(df: pd.DataFrame) -> list[dict]:
    recommendations: list[dict] = []
    if df.empty:
        return recommendations

    if "sleep_hours" in df.columns and "energy_level" in df.columns:
        sample = df[["sleep_hours", "energy_level"]].dropna()
        if len(sample) >= 5:
            corr = sample["sleep_hours"].corr(sample["energy_level"])
            if corr is not None and not np.isnan(corr) and corr > 0.3:
                recommendations.append(
                    {
                        "message": "Увеличение сна связано с ростом энергии. "
                        "Попробуйте добавить +30–60 мин сна.",
                        "severity": "info",
                    }
                )

    if "deep_work_hours" in df.columns and "wellbeing" in df.columns:
        sample = df[["deep_work_hours", "wellbeing"]].dropna()
        if len(sample) >= 5:
            corr = sample["deep_work_hours"].corr(sample["wellbeing"])
            if corr is not None and not np.isnan(corr) and corr < -0.3:
                recommendations.append(
                    {
                        "message": "Повышенная концентрация без отдыха связана "
                        "с более низким самочувствием. Планируйте перерывы.",
                        "severity": "warning",
                    }
                )

    if "expense_food" in df.columns and "wellbeing" in df.columns:
        sample = df[["expense_food", "wellbeing"]].dropna()
        if len(sample) >= 5:
            corr = sample["expense_food"].corr(sample["wellbeing"])
            if corr is not None and not np.isnan(corr) and corr < -0.3:
                recommendations.append(
                    {
                        "message": "Расходы на питание связаны с самочувствием. "
                        "Стоит пересмотреть рацион или бюджет.",
                        "severity": "info",
                    }
                )

    if not recommendations:
        recommendations.append(
            {
                "message": "Продолжайте регулярный трекинг — скоро появятся персональные рекомендации.",
                "severity": "info",
            }
        )

    return recommendations


def recommendations_payload(df: pd.DataFrame) -> dict:
    return {
        "generated_at": datetime.utcnow(),
        "recommendations": generate_recommendations(df),
    }
