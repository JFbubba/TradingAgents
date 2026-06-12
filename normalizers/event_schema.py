"""Normalized event schema for exchange intelligence events."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class ExchangeEvent:
    source_platform: str
    source_type: str
    event_type: str
    raw_title: str
    url: str
    asset: str = "UNKNOWN"
    pairs: list[str] = field(default_factory=list)
    market: str = "unknown"
    published_at_utc: str | None = None
    effective_at_utc: str | None = None
    impact_score: int = 0
    confidence: float = 1.0
    summary: str = ""
    detected_at_utc: str = field(default_factory=utc_now_iso)
    raw_payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
