import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser

# Medium RSS feeds by AI-related tags
_DEFAULT_TAGS = [
    "artificial-intelligence",
    "machine-learning",
    "llm",
    "generative-ai",
    "deep-learning",
]


def _fetch_feed(tag: str) -> list[dict]:
    feed = feedparser.parse(f"https://medium.com/feed/tag/{tag}")
    results = []
    for entry in feed.entries:
        try:
            published = parsedate_to_datetime(entry.published)
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        except Exception:
            published = datetime.now(timezone.utc)

        results.append({
            "title": entry.title,
            "url": entry.link,
            "author": getattr(entry, "author", "Unknown"),
            "published": published,
            "tags": [t.term for t in getattr(entry, "tags", [])],
        })
    return results


def search_articles(query: str, max_results: int = 5, hours: int = 24) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    keywords = [w.lower() for w in re.split(r"\s+", query.strip()) if len(w) > 1]

    # Collect articles from default tags
    seen_urls: set[str] = set()
    all_articles: list[dict] = []
    for tag in _DEFAULT_TAGS:
        for article in _fetch_feed(tag):
            if article["url"] in seen_urls:
                continue
            seen_urls.add(article["url"])
            all_articles.append(article)

    # Filter by time window
    recent = [a for a in all_articles if a["published"] >= cutoff]

    # If a custom query is given, score by keyword match; otherwise return as-is
    if keywords:
        def _score(article: dict) -> int:
            text = (article["title"] + " " + " ".join(article["tags"])).lower()
            return sum(1 for kw in keywords if kw in text)

        recent.sort(key=_score, reverse=True)

    return recent[:max_results]
