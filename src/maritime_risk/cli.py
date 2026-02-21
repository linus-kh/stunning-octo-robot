from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maritime-risk",
        description="Bewertet Logistikrisiko für Seefracht aus frei zugänglichen APIs.",
    )
    parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    assessment = run_pipeline()

    if args.json:
        print(json.dumps(asdict(assessment), default=str, ensure_ascii=False, indent=2))
        return

    print(assessment.summary)
    print("\nEinzelmetriken:")
    for obs in assessment.observations:
        trend = "↑ Risiko" if obs.higher_is_riskier else "↓ Risiko"
        print(f"- {obs.source}: {obs.metric}={obs.value} {obs.unit} ({trend})")

    if assessment.warnings:
        print("\nWarnungen:")
        for warning in assessment.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
