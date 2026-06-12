"""Telegram alert client for exchange intelligence events."""

from __future__ import annotations

import requests


def format_alert(event: dict) -> str:
    score = event.get("impact_score", 0)
    platform = str(event.get("source_platform", "unknown")).upper()
    event_type = event.get("event_type", "unknown")
    title = event.get("raw_title", "")
    url = event.get("url", "")
    detected = event.get("detected_at_utc", "")

    return (
        f"[{score}] {platform} — {event_type}\n\n"
        f"Title: {title}\n"
        f"URL: {url}\n"
        f"Detected: {detected}"
    )


class TelegramAlerter:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is missing")
        if not chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is missing")
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_event(self, event: dict) -> None:
        message = format_alert(event)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        response = requests.post(
            url,
            json={
                "chat_id": self.chat_id,
                "text": message,
                "disable_web_page_preview": False,
            },
            timeout=20,
        )
        response.raise_for_status()
