from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class MetricObservation:
    source: str
    metric: str
    value: float
    unit: str
    observed_at: datetime
    higher_is_riskier: bool = True
    note: str = ""


@dataclass(slots=True)
class RiskAssessment:
    score: float
    level: str
    summary: str
    observations: list[MetricObservation]
    warnings: list[str]
