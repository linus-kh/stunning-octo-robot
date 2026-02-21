from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from .models import MetricObservation


@dataclass(slots=True)
class SourceResult:
    observations: list[MetricObservation]
    warnings: list[str]


class BaseSource:
    name: str

    def fetch(self) -> SourceResult:
        raise NotImplementedError

    @staticmethod
    def _get_json(url: str, params: dict[str, str] | None = None) -> dict | list:
        query = f"?{urlencode(params)}" if params else ""
        with urlopen(f"{url}{query}", timeout=20) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)

    @staticmethod
    def _age_days_from_epoch_ms(epoch_ms: int | float) -> float:
        observed = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
        return float(max((datetime.now(timezone.utc) - observed).days, 0))

    @staticmethod
    def _age_days_from_iso(iso_value: str) -> float:
        observed = datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
        return float(max((datetime.now(timezone.utc) - observed).days, 0))


class PortWatchSource(BaseSource):
    name = "PortWatch"

    def fetch(self) -> SourceResult:
        try:
            data = self._get_json(
                "https://portwatch.imf.org/api/search/v1",
                {"limit": "1", "filter": "type:Dataset"},
            )
            modified_ms = data["item"]["properties"]["modified"]
            age_days = self._age_days_from_epoch_ms(modified_ms)
            obs = MetricObservation(
                source=self.name,
                metric="data_age_days",
                value=age_days,
                unit="days",
                observed_at=datetime.now(timezone.utc),
                higher_is_riskier=True,
                note="Ältere Hafenaktivitätsdaten erhöhen Unsicherheit.",
            )
            return SourceResult([obs], [])
        except (HTTPError, URLError, KeyError, IndexError, ValueError, TimeoutError) as exc:
            return SourceResult([], [f"{self.name}: API konnte nicht gelesen werden ({exc})."])


class MarineCadastreSource(BaseSource):
    name = "MarineCadastre"

    def fetch(self) -> SourceResult:
        try:
            data = self._get_json(
                "https://hub.marinecadastre.gov/api/search/v1",
                {"limit": "1", "q": "marine traffic"},
            )
            modified_ms = data["item"]["properties"]["modified"]
            age_days = self._age_days_from_epoch_ms(modified_ms)
            obs = MetricObservation(
                source=self.name,
                metric="data_age_days",
                value=age_days,
                unit="days",
                observed_at=datetime.now(timezone.utc),
                higher_is_riskier=True,
                note="Veraltete Lage-/Grenzdaten können Routingrisiken erhöhen.",
            )
            return SourceResult([obs], [])
        except (HTTPError, URLError, KeyError, ValueError, TimeoutError) as exc:
            return SourceResult([], [f"{self.name}: API konnte nicht gelesen werden ({exc})."])


class CopernicusSource(BaseSource):
    name = "Copernicus"

    def fetch(self) -> SourceResult:
        try:
            started = time.perf_counter()
            data = self._get_json(
                "https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                {"$top": "1", "$select": "Id"},
            )
            _ = data["value"][0]["Id"]
            latency_seconds = round(time.perf_counter() - started, 3)
            obs = MetricObservation(
                source=self.name,
                metric="api_latency_seconds",
                value=latency_seconds,
                unit="seconds",
                observed_at=datetime.now(timezone.utc),
                higher_is_riskier=True,
                note="Höhere API-Latenz reduziert Aktualität der Satellitensignale.",
            )
            return SourceResult([obs], [])
        except (HTTPError, URLError, KeyError, IndexError, ValueError, TimeoutError) as exc:
            return SourceResult([], [f"{self.name}: API konnte nicht gelesen werden ({exc})."])


class WorldBankSource(BaseSource):
    name = "WorldBank"

    def fetch(self) -> SourceResult:
        try:
            data = self._get_json(
                "https://api.worldbank.org/v2/country/WLD/indicator/IS.SHP.GOOD.TU",
                {"format": "json", "per_page": "5"},
            )
            rows = data[1]
            latest = next((row for row in rows if row.get("value") is not None), None)
            if not latest:
                raise ValueError("Kein Wert für IS.SHP.GOOD.TU gefunden")
            value = float(latest["value"])
            obs = MetricObservation(
                source=self.name,
                metric="goods_transport_volume",
                value=value,
                unit="million ton-km",
                observed_at=datetime.now(timezone.utc),
                higher_is_riskier=True,
                note="Höheres Volumen kann Engpässe und Verzögerungsrisiko erhöhen.",
            )
            return SourceResult([obs], [])
        except (HTTPError, URLError, KeyError, IndexError, ValueError, TimeoutError) as exc:
            return SourceResult([], [f"{self.name}: API konnte nicht gelesen werden ({exc})."])


def default_sources() -> list[BaseSource]:
    return [
        PortWatchSource(),
        MarineCadastreSource(),
        CopernicusSource(),
        WorldBankSource(),
    ]
