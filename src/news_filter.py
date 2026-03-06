from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

from rss_reader import NewsItem


AI_KEYWORDS = {
    "ai": 2,
    "artificial intelligence": 3,
    "machine learning": 3,
    "llm": 3,
    "gpt": 3,
    "gemini": 3,
    "claude": 3,
    "openai": 3,
    "anthropic": 3,
    "deepseek": 3,
    "model": 1,
    "agent": 2,
    "inference": 2,
    "reasoning": 2,
}

SOURCE_BONUS = {
    "hacker news": 2,
    "openai": 3,
    "anthropic": 3,
}

SECTION_KEYWORDS: Dict[str, Set[str]] = {
    "models": {"model", "llm", "gpt", "gemini", "claude", "benchmark", "inference"},
    "products": {"launch", "product", "feature", "release", "copilot", "assistant", "app"},
    "research": {"paper", "research", "study", "arxiv", "method", "training"},
    "policy": {"policy", "regulation", "law", "government", "compliance", "safety"},
    "business": {"funding", "acquisition", "revenue", "partnership", "startup", "market"},
    "tools": {"sdk", "api", "framework", "library", "agent", "workflow", "open source"},
}

ALLOWED_SECTIONS = ["models", "products", "research", "policy", "business", "tools", "other"]


def _normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff ]+", "", text)
    return text


def _canonical_link(link: str) -> str:
    parsed = urlparse(link)
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{path}".lower()


def _title_fingerprint(title: str) -> str:
    normalized = _normalize_text(title)
    tokens = [tok for tok in normalized.split(" ") if tok]
    return " ".join(tokens[:14])


def classify_section(item: NewsItem) -> str:
    text = f"{item.title} {item.summary}".lower()
    best_section = "other"
    best_score = 0

    for section, keywords in SECTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > best_score:
            best_score = score
            best_section = section

    return best_section


def is_ai_related(item: NewsItem) -> bool:
    text = f"{item.title} {item.summary}".lower()
    return any(keyword in text for keyword in AI_KEYWORDS)


def _score_item(item: NewsItem, now: datetime) -> int:
    text = f"{item.title} {item.summary}".lower()
    score = 0

    for keyword, weight in AI_KEYWORDS.items():
        if keyword in text:
            score += weight

    source_lower = item.source.lower()
    for source_name, bonus in SOURCE_BONUS.items():
        if source_name in source_lower:
            score += bonus

    if item.published:
        age_hours = (now - item.published).total_seconds() / 3600
        if age_hours <= 24:
            score += 3
        elif age_hours <= 48:
            score += 1

    title_len = len(item.title.strip())
    if 20 <= title_len <= 140:
        score += 1

    return score


def deduplicate(items: List[NewsItem]) -> List[NewsItem]:
    seen_links: Set[str] = set()
    seen_titles: Set[str] = set()
    unique: List[NewsItem] = []

    for item in items:
        link_key = _canonical_link(item.link)
        title_key = _title_fingerprint(item.title)

        if link_key in seen_links or title_key in seen_titles:
            continue

        seen_links.add(link_key)
        seen_titles.add(title_key)
        unique.append(item)

    return unique


def parse_sections(raw_sections: str) -> List[str]:
    if not raw_sections.strip() or raw_sections.strip().lower() == "all":
        return []
    sections = [sec.strip().lower() for sec in raw_sections.split(",") if sec.strip()]
    return [sec for sec in sections if sec in ALLOWED_SECTIONS]


def filter_by_sections(items: List[NewsItem], selected_sections: List[str]) -> List[NewsItem]:
    if not selected_sections:
        return items
    return [item for item in items if classify_section(item) in selected_sections]


def count_sections(items: List[NewsItem]) -> Dict[str, int]:
    counts = {section: 0 for section in ALLOWED_SECTIONS}
    for item in items:
        counts[classify_section(item)] += 1
    return counts


def filter_news(items: List[NewsItem], max_items: int = 12) -> List[NewsItem]:
    now = datetime.now(timezone.utc)
    unique = deduplicate(items)
    ai_related = [item for item in unique if is_ai_related(item)]
    pool = ai_related if ai_related else unique

    scored: List[Tuple[int, NewsItem]] = [(_score_item(item, now), item) for item in pool]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:max_items]]
