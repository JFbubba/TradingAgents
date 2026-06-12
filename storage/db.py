"""SQLite storage and deduplication for exchange intelligence events."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_hash TEXT UNIQUE NOT NULL,
    source_platform TEXT NOT NULL,
    event_type TEXT NOT NULL,
    raw_title TEXT NOT NULL,
    url TEXT NOT NULL,
    impact_score INTEGER NOT NULL,
    detected_at_utc TEXT NOT NULL,
    raw_json TEXT NOT NULL
);
"""


def event_hash(event: dict[str, Any]) -> str:
    base = "|".join(
        [
            str(event.get("source_platform", "")),
            str(event.get("raw_title", "")),
            str(event.get("url", "")),
        ]
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


class EventStore:
    def __init__(self, database_path: str = "storage/events.sqlite") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute(SCHEMA)
        self.connection.commit()

    def insert_event(self, event: dict[str, Any]) -> bool:
        digest = event_hash(event)
        try:
            self.connection.execute(
                """
                INSERT INTO events (
                    event_hash,
                    source_platform,
                    event_type,
                    raw_title,
                    url,
                    impact_score,
                    detected_at_utc,
                    raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    digest,
                    event.get("source_platform", "unknown"),
                    event.get("event_type", "unknown"),
                    event.get("raw_title", ""),
                    event.get("url", ""),
                    int(event.get("impact_score", 0)),
                    event.get("detected_at_utc", ""),
                    json.dumps(event, ensure_ascii=False, sort_keys=True),
                ),
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def close(self) -> None:
        self.connection.close()
