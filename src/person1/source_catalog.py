from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    source_name: str
    tier: str
    domain: str
    primary_url: str
    terms_url: str
    region_scope: str
    backup_rank: int


SOURCE_CATALOG = [
    SourceDefinition(
        source_id="usgs_eq",
        source_name="USGS Earthquake Hazards Program",
        tier="tier_a",
        domain="earthquake",
        primary_url="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
        terms_url="https://www.usgs.gov/information-policies-and-notices",
        region_scope="global",
        backup_rank=1,
    ),
    SourceDefinition(
        source_id="noaa_alerts",
        source_name="NOAA National Weather Service Alerts",
        tier="tier_a",
        domain="weather",
        primary_url="https://api.weather.gov/alerts/active",
        terms_url="https://www.weather.gov/disclaimer",
        region_scope="us",
        backup_rank=1,
    ),
    SourceDefinition(
        source_id="fema",
        source_name="FEMA Open Data",
        tier="tier_a",
        domain="federal_disaster",
        primary_url="https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries",
        terms_url="https://www.fema.gov/about/openfema/terms-and-conditions",
        region_scope="us",
        backup_rank=1,
    ),
    SourceDefinition(
        source_id="gdacs",
        source_name="GDACS",
        tier="tier_b",
        domain="multi_hazard",
        primary_url="https://www.gdacs.org/xml/rss.xml",
        terms_url="https://www.gdacs.org/About/info.aspx",
        region_scope="global",
        backup_rank=2,
    ),
    SourceDefinition(
        source_id="reliefweb",
        source_name="ReliefWeb",
        tier="tier_b",
        domain="humanitarian",
        primary_url="https://api.reliefweb.int/v1/reports?appname=person1",
        terms_url="https://reliefweb.int/terms-conditions",
        region_scope="global",
        backup_rank=2,
    ),
]

