"""Simple deterministic impact scoring for exchange announcements."""

from __future__ import annotations


def classify_event_type(title: str) -> str:
    text = title.lower()

    if any(word in text for word in ["delist", "delisting", "remove", "removal", "cease trading"]):
        if any(word in text for word in ["futures", "perpetual", "perp", "contract"]):
            return "delisting_futures"
        return "delisting_spot"

    if "withdraw" in text and any(word in text for word in ["suspend", "suspension", "maintenance"]):
        return "withdrawal_suspension"

    if "deposit" in text and any(word in text for word in ["suspend", "suspension", "maintenance"]):
        return "deposit_suspension"

    if any(word in text for word in ["list", "listing", "launch", "opens trading", "new trading pair", "added"]):
        if any(word in text for word in ["futures", "perpetual", "perp", "contract"]):
            return "listing_futures"
        return "listing_spot"

    if any(word in text for word in ["maintenance", "upgrade", "system upgrade", "wallet maintenance"]):
        return "maintenance"

    if any(word in text for word in ["api", "websocket", "rate limit", "endpoint", "changelog"]):
        return "api_change"

    if any(word in text for word in ["migration", "swap", "rebrand", "ticker change"]):
        return "token_migration"

    return "unknown"


def score_event(platform: str, event_type: str, title: str = "") -> int:
    platform = platform.lower()
    text = title.lower()

    if event_type == "delisting_futures":
        return 95
    if event_type == "delisting_spot":
        return 90
    if event_type == "withdrawal_suspension":
        return 85
    if event_type == "listing_futures":
        return 80
    if event_type == "listing_spot":
        if platform in {"binance", "coinbase", "upbit", "bithumb"}:
            return 85
        return 75
    if event_type == "maintenance":
        if any(word in text for word in ["matching engine", "futures", "system upgrade"]):
            return 80
        return 75
    if event_type == "deposit_suspension":
        return 75
    if event_type == "api_change":
        return 70
    if event_type == "token_migration":
        return 60

    return 20
