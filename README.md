# ai-news-digest

每天从 RSS 抓取 AI 新闻，自动输出日报。

## 新功能

- 支持输出格式：`md` / `txt` / `json`
- 支持按板块筛选：`models, products, research, policy, business, tools, other`

## 安装

```bash
cd C:\Users\xuyid\ai-news-digest
pip install -r requirements.txt
```

## 配置

```bash
copy .env.example .env
```

编辑 `.env`：

```env
LLM_API_KEY=your_key_here
LLM_BASE_URL=https://your-provider.example/v1
LLM_MODEL=gpt-4o-mini
```

## 运行

默认（Markdown）：

```bash
python src/main.py
```

输出 txt：

```bash
python src/main.py --format txt
```

输出 json：

```bash
python src/main.py --format json
```

只看某些板块：

```bash
python src/main.py --sections models,research
```

组合示例（只看 models + research，并输出 txt）：

```bash
python src/main.py --sections models,research --format txt
```

输出文件路径：

- `output/daily_ai_news_YYYYMMDD.md`
- `output/daily_ai_news_YYYYMMDD.txt`
- `output/daily_ai_news_YYYYMMDD.json`

## 一键推送到 GitHub

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish_to_github.ps1 -RepoUrl "https://github.com/Furfurdo/ProjectP.git" -Message "feat: update daily digest"
```
