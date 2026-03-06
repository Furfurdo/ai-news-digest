from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from markdown_writer import build_json, build_markdown, build_text
from news_filter import (
    ALLOWED_SECTIONS,
    classify_section,
    count_sections,
    deduplicate,
    filter_by_sections,
    filter_news,
    parse_sections,
)
from rss_reader import fetch_rss_items, load_sources
from summarizer import summarize_news


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI News Digest generator")
    parser.add_argument("--sources", default="rss_sources.txt", help="RSS source list path")
    parser.add_argument("--days", type=int, default=2, help="Only include items from recent N days")
    parser.add_argument(
        "--max-items",
        type=int,
        default=12,
        help="Max items kept before LLM summarization",
    )
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument(
        "--format",
        choices=["md", "txt", "json"],
        default="md",
        help="Output format: md, txt, json",
    )
    parser.add_argument(
        "--sections",
        default="all",
        help=(
            "Comma-separated sections to keep. "
            f"Use 'all' or choose from: {', '.join(ALLOWED_SECTIONS)}"
        ),
    )
    return parser.parse_args()


def _render(format_name: str, digest: dict, now: datetime, section_counts: dict) -> str:
    if format_name == "txt":
        return build_text(digest, now, section_counts)
    if format_name == "json":
        return build_json(digest, now, section_counts)
    return build_markdown(digest, now, section_counts)


def main() -> int:
    args = parse_args()
    now = datetime.now()
    selected_sections = parse_sections(args.sections)

    try:
        print("Loading RSS sources...")
        urls = load_sources(args.sources)
        if not urls:
            print("No RSS source found. Check your sources file.")
            return 1

        print("Fetching feed entries...")
        raw_items = fetch_rss_items(urls=urls, days=args.days)
        unique_items = deduplicate(raw_items)
        ranked_items = filter_news(raw_items, max_items=args.max_items)
        section_filtered_items = filter_by_sections(ranked_items, selected_sections)

        print(
            f"Fetched={len(raw_items)}, Unique={len(unique_items)}, "
            f"Ranked={len(ranked_items)}, AfterSectionFilter={len(section_filtered_items)}"
        )

        if selected_sections:
            print(f"Selected sections: {', '.join(selected_sections)}")

        section_map = {item.link: classify_section(item) for item in section_filtered_items}
        section_counts = count_sections(section_filtered_items)

        print("Summarizing selected items...")
        digest = summarize_news(section_filtered_items, section_map=section_map)

        content = _render(args.format, digest, now, section_counts)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"daily_ai_news_{now.strftime('%Y%m%d')}.{args.format}"
        output_path.write_text(content, encoding="utf-8")

        print(f"Done. Output saved to: {output_path}")
        return 0
    except Exception as exc:
        print(f"Failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
