from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
import feedparser
import hashlib

load_dotenv()
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')

def fetch_news(query: str = "SRAG OR síndrome respiratória OR doença respiratória OR gripe",
               days: int = 7,
               language: str = "pt") -> list[dict]:
    """
    Retorna lista de notícias formatadas para RAG:
    [
      {
        "id": "...",          # hash ou url
        "title": "...",
        "content": "...",
        "url": "...",
        "published": "..."
      }
    ]
    """
    if NEWSAPI_KEY:
        return _fetch_news_newsapi(query, days, language)
    else:
        return _fetch_news_rss(query)

def _make_id(text: str) -> str:
    """Gera um id único a partir do texto (hash md5)"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def _fetch_news_newsapi(query: str, days: int, language: str) -> list[dict]:
    base_url = "https://newsapi.org/v2/everything"
    date_from = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    params = {
        "q": query,
        "from": date_from,
        "language": language,
        "sortBy": "publishedAt",
        "pageSize": 50,
    }
    headers = {"Authorization": NEWSAPI_KEY}
    r = requests.get(base_url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    articles = []
    for a in data.get("articles", []):
        content = f"{a.get('description') or ''} {a.get('content') or ''}".strip()
        articles.append({
            "id": _make_id(a.get("url") or content),
            "title": a.get("title") or "",
            "content": content,
            "url": a.get("url") or "",
            "published": a.get("publishedAt") or ""
        })
    return articles

def _fetch_news_rss(query: str) -> list[dict]:
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(rss_url)
    articles = []
    for e in feed.entries[:50]:
        content = getattr(e, "summary", "")
        url = getattr(e, "link", "")
        articles.append({
            "id": _make_id(url or content),
            "title": getattr(e, "title", ""),
            "content": content,
            "url": url,
            "published": getattr(e, "published", "")
        })
    return articles

if __name__ == "__main__":
    print("NEWSAPI_KEY carregada:", NEWSAPI_KEY is not None)
    articles = fetch_news(days=3)
    print(f"Foram encontradas {len(articles)} notícias.")
    if articles:
        print("Exemplo:", articles[0])