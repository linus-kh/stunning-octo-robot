# Maritime Logistics Risk (Seefracht)

Dieses Projekt baut einen **offenen Risiko-Score für Seefracht-Logistik** auf Basis frei zugänglicher APIs.

## Verwendete Datenquellen (ohne API-Key)

- **PortWatch (IMF)**: Open Search API für Datensatz-Metadaten (`/api/search/v1/items`)
- **MarineCadastre**: Hub Search API (`/api/search/v1`)
- **Copernicus Data Space**: OData-Katalog (`/odata/v1/Products`)
- **World Bank Data360/API**: Weltbank-Indikator-API (`api.worldbank.org`)

## Ziel

Die Pipeline lädt aktuelle Signale aus den APIs, normalisiert sie und berechnet daraus einen Score von `0..100`:

- `0-34`: niedriges Risiko
- `35-64`: mittleres Risiko
- `65-100`: hohes Risiko

> Hinweis: Der Score ist ein Frühwarnsignal und ersetzt keine operative Lagebewertung.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Nutzung

```bash
maritime-risk
maritime-risk --json
```

## Projektstruktur

- `src/maritime_risk/sources.py`: API-Adapter pro Quelle
- `src/maritime_risk/scoring.py`: Normalisierung + Risiko-Klassifikation
- `src/maritime_risk/pipeline.py`: Orchestrierung
- `src/maritime_risk/cli.py`: Kommandozeilen-Interface

## Erweiterungen

- Zusätzliche APIs (AIS, Wetter, Versicherungsdaten) als weitere `Source`-Klassen ergänzen.
- Gewichte pro Metrik in `scoring.py` feinjustieren.
- Ergebnisse periodisch speichern (DB) und Trendanalyse aufbauen.
