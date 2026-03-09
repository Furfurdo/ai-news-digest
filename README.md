# ai-news-digest

Generate a daily AI news digest from RSS feeds.

## Features

- Fetches AI news from RSS sources
- Deduplicates and ranks stories
- Filters by sections:
  - `models`, `products`, `research`, `policy`, `business`, `tools`, `other`
- Summarizes with an OpenAI-compatible API
- Outputs in `md`, `txt`, or `json`

## Requirements

- Python 3.10+
- A provider API key (OpenAI-compatible endpoint)

## Install

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy env template:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
copy .env.example .env
```

2. Edit `.env`:

```env
LLM_API_KEY=your_key_here
LLM_BASE_URL=https://your-provider.example/v1
LLM_MODEL=gpt-4o-mini
```

## RSS Sources

Edit `rss_sources.txt`, one feed URL per line.

## Usage

Default (Markdown):

```bash
python src/main.py
```

Output format:

```bash
python src/main.py --format txt
python src/main.py --format json
```

Filter sections:

```bash
python src/main.py --sections models,research
```

Combine options:

```bash
python src/main.py --sections models,research --format txt --days 1 --max-items 10
```

## Output Files

- `output/daily_ai_news_YYYYMMDD.md`
- `output/daily_ai_news_YYYYMMDD.txt`
- `output/daily_ai_news_YYYYMMDD.json`

## Publish to GitHub

Use the helper script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish_to_github.ps1 -RepoUrl "https://github.com/<your-user>/<your-repo>.git" -Message "chore: update digest"
```
