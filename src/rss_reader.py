from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

import feedparser


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    published: datetime | None
    summary: str


def load_sources(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def _to_datetime(entry) -> datetime | None:
    if not getattr(entry, "published_parsed", None):
        return None
    tm = entry.published_parsed
    return datetime(*tm[:6], tzinfo=timezone.utc)


def fetch_rss_items(urls: List[str], days: int = 2, limit_per_feed: int = 15) -> List[NewsItem]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    results: List[NewsItem] = []

    for url in urls:
        parsed = feedparser.parse(url)
        source_title = getattr(parsed.feed, "title", url)
        count = 0

        for entry in parsed.entries:
            if count >= limit_per_feed:
                break

            published = _to_datetime(entry)
            if published and published < cutoff:
                continue

            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            summary = getattr(entry, "summary", "").strip()

            if not title or not link:
                continue

            results.append(
                NewsItem(
                    title=title,
                    link=link,
                    source=source_title,
                    published=published,
                    summary=summary,
                )
            )
            count += 1

    return results
