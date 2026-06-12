"""Binance announcement collector.

Read-only collector for Binance public announcement data.
The Binance announcement payload shape changes over time, so extraction is recursive
and tolerant instead of assuming one fixed JSON structure.
"""

from __future__ import annotations

from typing import Any

import requests

from normalizers.event_schema import ExchangeEvent
from scoring.impact_score import classify_event_type, score_event


BINANCE_ENDPOINTS = [
    "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
    "https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query",
]

# Known/high-value catalog IDs. Binance may change names/IDs; extraction is tolerant.
CATEGORY_IDS = {
    "latest": 49,
    "new_crypto_listing": 48,
    "delisting": 161,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 TradingAgents-ExchangeIntelRadar/0.1",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
}


def _looks_like_article(item: dict[str, Any]) -> bool:
    title = item.get("title")
    code = item.get("code") or item.get("id")
    return isinstance(title, str) and bool(title.strip()) and code is not None


def _extract_articles_recursive(payload: Any) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []

    if isinstance(payload, dict):
        if _looks_like_article(payload):
            articles.append(payload)

        for value in payload.values():
            articles.extend(_extract_articles_recursive(value))

    elif isinstance(payload, list):
        for value in payload:
            articles.extend(_extract_articles_recursive(value))

    return articles


def _dedupe_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []

    for article in articles:
        title = str(article.get("title") or "").strip()
        code = str(article.get("code") or article.get("id") or "").strip()
        key = f"{code}|{title}"
        if not title or key in seen:
            continue
        seen.add(key)
        output.append(article)

    return output


def _fetch_payload(endpoint: str, category_id: int, size: int) -> dict[str, Any] | None:
    params = {
        "type": 1,
        "catalogId": category_id,
        "pageNo": 1,
        "pageSize": size,
    }

    try:
        response = requests.get(endpoint, params=params, headers=HEADERS, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"Binance fetch failed: endpoint={endpoint} category_id={category_id} error={exc}")
        return None


def _fetch_articles(size: int = 10) -> list[dict[str, Any]]:
    all_articles: list[dict[str, Any]] = []

    for category_name, category_id in CATEGORY_IDS.items():
        for endpoint in BINANCE_ENDPOINTS:
            payload = _fetch_payload(endpoint=endpoint, category_id=category_id, size=size)
            if not payload:
                continue

            articles = _extract_articles_recursive(payload)
            for article in articles:
                article["_radar_category"] = category_name
                article["_radar_endpoint"] = endpoint
            all_articles.extend(articles)

    return _dedupe_articles(all_articles)


def _article_url(article: dict[str, Any]) -> str:
    code = str(article.get("code") or article.get("id") or "").strip()
    if code.startswith("http"):
        return code
    if code:
        return f"https://www.binance.com/en/support/announcement/{code}"
    return "https://www.binance.com/en/support/announcement"


def collect_binance_announcements(size: int = 10) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    articles = _fetch_articles(size=size)
    print(f"Binance articles fetched: {len(articles)}")

    for article in articles:
        title = str(article.get("title") or "").strip()
        if not title:
            continue

        event_type = classify_event_type(title)
        impact_score = score_event("binance", event_type, title)

        event = ExchangeEvent(
            source_platform="binance",
            source_type="official_announcement",
            event_type=event_type,
            raw_title=title,
            url=_article_url(article),
            impact_score=impact_score,
            summary=title,
            raw_payload={
                "category": article.get("_radar_category", "unknown"),
                "endpoint": article.get("_radar_endpoint", "unknown"),
                "article": article,
            },
        )
        events.append(event.to_dict())

    return events
