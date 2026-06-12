"""Binance announcement collector.

This collector uses Binance public announcement API endpoints when available.
It intentionally stays read-only and does not require Binance credentials.
"""

from __future__ import annotations

from typing import Any

import requests

from normalizers.event_schema import ExchangeEvent
from scoring.impact_score import classify_event_type, score_event


BINANCE_ANNOUNCEMENTS_URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"


CATEGORY_IDS = {
    "latest": 0,
    "delisting": 161,
}


def _fetch_articles(category_id: int = 0, size: int = 10) -> list[dict[str, Any]]:
    params = {
        "type": 1,
        "catalogId": category_id,
        "pageNo": 1,
        "pageSize": size,
    }
    headers = {
        "User-Agent": "TradingAgents-ExchangeIntelRadar/0.1",
        "Accept": "application/json,text/plain,*/*",
    }
    response = requests.get(BINANCE_ANNOUNCEMENTS_URL, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    payload = response.json()

    data = payload.get("data") or {}
    articles = data.get("articles") or []
    if not isinstance(articles, list):
        return []
    return articles


def collect_binance_announcements(size: int = 10) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    for category_name, category_id in CATEGORY_IDS.items():
        for article in _fetch_articles(category_id=category_id, size=size):
            title = str(article.get("title") or "").strip()
            if not title:
                continue

            code = article.get("code") or article.get("id") or ""
            url = f"https://www.binance.com/en/support/announcement/{code}" if code else "https://www.binance.com/en/support/announcement"

            event_type = classify_event_type(title)
            impact_score = score_event("binance", event_type, title)

            event = ExchangeEvent(
                source_platform="binance",
                source_type="official_announcement",
                event_type=event_type,
                raw_title=title,
                url=url,
                impact_score=impact_score,
                summary=title,
                raw_payload={
                    "category": category_name,
                    "article": article,
                },
            )
            events.append(event.to_dict())

    return events
