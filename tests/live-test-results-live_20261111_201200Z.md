# Live Retrieval Results (live_20261111_201200Z)

- **Run ID:** `live_20261111_201200Z`
- **Generated (UTC):** 2026-11-11T20:12:01Z
- **Input claims file:** `data/live/input-claims-live_20261111_201200Z.json`
- **Validated output file:** `data/live/validated-output-live_20261111_201200Z.json`
- **Schema validation:** PASS

## Source Fetch Log

| Source | HTTP | Latency (ms) | Parsed records | Error | Raw file |
|---|---:|---:|---:|---|---|
| USGS Earthquake Hazards Program | 200 | 132 | 6 | None | `data/live/raw/live_20261111_201200Z/usgs_eq.json` |
| NOAA National Weather Service Alerts | 200 | 503 | 8 | None | `data/live/raw/live_20261111_201200Z/noaa_alerts.json` |
| FEMA Open Data | 200 | 219 | 8 | None | `data/live/raw/live_20261111_201200Z/fema_disasters.json` |

## Output Record Count
- `22` records in validated output
