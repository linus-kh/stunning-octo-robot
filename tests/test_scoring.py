import unittest
from datetime import datetime, timezone

from maritime_risk.models import MetricObservation
from maritime_risk.scoring import assess_risk


class ScoringTests(unittest.TestCase):
    def _obs(self, metric: str, value: float, riskier: bool) -> MetricObservation:
        return MetricObservation(
            source="test",
            metric=metric,
            value=value,
            unit="u",
            observed_at=datetime.now(timezone.utc),
            higher_is_riskier=riskier,
        )

    def test_assess_risk_with_no_observations(self):
        result = assess_risk([], ["warn"])
        self.assertEqual(result.score, 50.0)
        self.assertEqual(result.level, "mittel")
        self.assertEqual(result.warnings, ["warn"])

    def test_assess_risk_high_when_risky_metrics_are_high(self):
        result = assess_risk([self._obs("data_age_days", 60, True)], [])
        self.assertEqual(result.level, "hoch")

    def test_assess_risk_low_when_protective_metrics_are_high(self):
        result = assess_risk([self._obs("product_count", 300000, False)], [])
        self.assertEqual(result.level, "niedrig")


if __name__ == "__main__":
    unittest.main()
