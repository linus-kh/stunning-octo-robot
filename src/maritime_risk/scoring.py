from __future__ import annotations

from .models import MetricObservation, RiskAssessment


def _normalize(observation: MetricObservation) -> float:
    baselines = {
        "data_age_days": 30.0,
        "dataset_count": 1000.0,
        "product_count": 100000.0,
        "api_latency_seconds": 3.0,
        "goods_transport_volume": 50000.0,
    }
    baseline = baselines.get(observation.metric, max(observation.value, 1.0))
    ratio = min(observation.value / baseline, 2.0)
    if observation.higher_is_riskier:
        return min(100.0, ratio * 50.0)
    return max(0.0, 100.0 - ratio * 50.0)


def assess_risk(observations: list[MetricObservation], warnings: list[str]) -> RiskAssessment:
    if not observations:
        return RiskAssessment(
            score=50.0,
            level="mittel",
            summary="Keine Messwerte verfügbar; konservativer Mittelwert genutzt.",
            observations=[],
            warnings=warnings,
        )

    component_scores = [_normalize(obs) for obs in observations]
    final_score = round(sum(component_scores) / len(component_scores), 2)

    if final_score < 35:
        level = "niedrig"
    elif final_score < 65:
        level = "mittel"
    else:
        level = "hoch"

    summary = (
        f"Aggregierter Risikoscore: {final_score}/100 ({level}). "
        "Die Aussage basiert auf offenen Datenquellen und ist als Frühwarnsignal zu verstehen."
    )
    return RiskAssessment(final_score, level, summary, observations, warnings)
