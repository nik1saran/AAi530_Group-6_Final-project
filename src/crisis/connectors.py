from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .source_catalog import SOURCE_CATALOG


@dataclass(frozen=True)
class FetchConfig:
    timeout_seconds: int = 20
    retries: int = 3
    backoff_seconds: float = 1.0
    user_agent: str = "crisis-verification-pipeline/1.0"


def fetch_json(url: str, cfg: FetchConfig) -> Any:
    headers = {"User-Agent": cfg.user_agent, "Accept": "application/json, application/geo+json"}
    last_error: Exception | None = None
    for attempt in range(cfg.retries):
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=cfg.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < cfg.retries - 1:
                time.sleep(cfg.backoff_seconds * (2 ** attempt))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def fetch_catalog_sources(cfg: FetchConfig | None = None) -> dict[str, Any]:
    config = cfg or FetchConfig()
    output: dict[str, Any] = {}
    for source in SOURCE_CATALOG:
        try:
            output[source.source_id] = {
                "source_name": source.source_name,
                "tier": source.tier,
                "url": source.primary_url,
                "payload": fetch_json(source.primary_url, config),
                "error": None,
            }
        except Exception as exc:  # explicit surfacing for source health monitoring
            output[source.source_id] = {
                "source_name": source.source_name,
                "tier": source.tier,
                "url": source.primary_url,
                "payload": None,
                "error": str(exc),
            }
    return output
