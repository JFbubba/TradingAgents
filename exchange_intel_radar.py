"""Exchange Intel Radar V0.1.

Read-only collector for exchange announcements.
Current scope: Binance official announcements + Telegram alerts.
"""

from __future__ import annotations

import os
from typing import Iterable

from dotenv import load_dotenv

from alerts.telegram import TelegramAlerter
from collectors.binance import collect_binance_announcements
from storage.db import EventStore


def parse_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def iter_events() -> Iterable[dict]:
    yield from collect_binance_announcements(size=10)


def main() -> None:
    load_dotenv()

    database_path = os.getenv("DATABASE_PATH", "storage/events.sqlite")
    alert_min_score = parse_int(os.getenv("ALERT_MIN_SCORE"), 70)
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    store = EventStore(database_path)
    alerter = None

    if telegram_token and telegram_chat_id:
        alerter = TelegramAlerter(telegram_token, telegram_chat_id)
    else:
        print("Telegram credentials missing. Events will be stored but not alerted.")

    inserted = 0
    alerted = 0

    try:
        for event in iter_events():
            is_new = store.insert_event(event)
            if not is_new:
                continue

            inserted += 1
            score = int(event.get("impact_score", 0))
            print(f"NEW [{score}] {event.get('source_platform')} — {event.get('raw_title')}")

            if alerter and score >= alert_min_score:
                alerter.send_event(event)
                alerted += 1
    finally:
        store.close()

    print(f"Done. Inserted={inserted}, Alerted={alerted}")


if __name__ == "__main__":
    main()
