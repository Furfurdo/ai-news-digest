from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Mapping, Optional

from dotenv import load_dotenv
from openai import OpenAI

from rss_reader import NewsItem

load_dotenv()


def _build_input(items: List[NewsItem], section_map: Optional[Mapping[str, str]] = None) -> str:
    lines = []
    for idx, item in enumerate(items, start=1):
        section = section_map.get(item.link, "other") if section_map else "other"
        lines.append(
            "\n".join(
                [
                    f"[{idx}] Title: {item.title}",
                    f"Source: {item.source}",
                    f"Section: {section}",
                    f"Link: {item.link}",
                    f"Snippet: {item.summary[:500]}",
                ]
            )
        )
    return "\n\n".join(lines)


def summarize_news(
    items: List[NewsItem],
    section_map: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    if not items:
        return {
            "daily_summary": "Today no usable AI news was collected.",
            "important_news": [],
            "key_takeaways": [],
        }

    api_key = os.getenv("LLM_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing LLM_API_KEY (or OPENAI_API_KEY).")

    model = os.getenv("LLM_MODEL", "").strip() or os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip() or os.getenv("OPENAI_BASE_URL", "").strip()
    client = OpenAI(api_key=api_key, base_url=base_url or None)

    system_prompt = (
        "You are a tech news editor. Summarize strictly from the provided items. "
        "Do not invent facts. Return valid JSON only."
    )
    user_prompt = (
        "Generate today's AI Daily Digest in Chinese with this JSON schema:\n"
        "{\n"
        '  "daily_summary": "string, 2-4 sentences",\n'
        '  "important_news": [\n'
        '    {"title":"string","brief":"string","source":"string","link":"string","section":"string"}\n'
        "  ],\n"
        '  "key_takeaways": ["string", "..."]\n'
        "}\n"
        "Constraints:\n"
        "- important_news: 5-8 items\n"
        "- key_takeaways: 3-5 items\n"
        "- Language: Chinese\n\n"
        f"News items:\n{_build_input(items, section_map)}"
    )

    completion = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = completion.choices[0].message.content or "{}"
    data = json.loads(content)
    data["model"] = model
    return data
