from __future__ import annotations

from .models import RiskAssessment
from .scoring import assess_risk
from .sources import BaseSource, default_sources


def run_pipeline(sources: list[BaseSource] | None = None) -> RiskAssessment:
    selected_sources = sources or default_sources()
    observations = []
    warnings = []

    for source in selected_sources:
        result = source.fetch()
        observations.extend(result.observations)
        warnings.extend(result.warnings)

    return assess_risk(observations, warnings)
