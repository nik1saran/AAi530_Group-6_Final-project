# Source Compliance, Jurisdiction Scope, and Fallback Strategy

## Jurisdiction Scope
- Primary operational scope: United States and globally significant catastrophic events.
- Source precedence is field-specific and depends on hazard domain.

## Field-Level Source Precedence
| Field | Primary Authority | Secondary Authority |
|---|---|---|
| Earthquake event facts | USGS | GDACS |
| Weather hazard status | NOAA/NWS/NHC | State emergency bulletins |
| Federal incident declarations | FEMA | State emergency management |
| Public health emergency guidance | CDC / WHO | Regional health agencies |
| Humanitarian context | ReliefWeb / GDACS | Institutional partner feeds |

## Source Terms and Licensing
All source usage must follow provider terms:
- USGS: information policy notices
- NOAA/NWS: weather service disclaimers
- FEMA OpenFEMA: published terms
- ReliefWeb and GDACS: platform terms

Reference links are maintained in `src/person1/source_catalog.py`.

## Fallback Order
1. Tier A source unavailable -> use alternate Tier A for same field domain.
2. If no Tier A is available -> use Tier B as preliminary only.
3. Tier C can be retained as unverified signal only; never promoted to confirmed.

## Data Retention and Purge
- Keep run manifests for audit traceability.
- Keep superseded records for timeline reconstruction.
- Purge malformed dead-letter records only after documented review.

