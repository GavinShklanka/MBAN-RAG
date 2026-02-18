from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.core.cache import HTTP_CACHE
from app.core.text import clean_text

BASE_WS = "https://wsearch.nlm.nih.gov/ws/query"
UA = {"User-Agent": "agentic-ai-rag/0.1"}

def medlineplus_search(query: str, max_topics: int = 5) -> List[Dict]:
    """
    Uses MedlinePlus search-based web service (XML response).
    Returns list of {title, url, snippet}
    """
    params = {
        "db": "healthTopics",
        "term": query,
        "retmax": str(max_topics),
    }
    cache_key = f"mplus_ws::{query}::{max_topics}"
    if cache_key in HTTP_CACHE:
        return HTTP_CACHE[cache_key]

    r = requests.get(BASE_WS, params=params, headers=UA, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "xml")
    docs = []
    for doc in soup.find_all("document"):
        url = doc.get("url") or ""
        title = (doc.find("content", {"name": "title"}).get_text(" ", strip=True)
                 if doc.find("content", {"name": "title"}) else "")
        snippet = (doc.find("content", {"name": "snippet"}).get_text(" ", strip=True)
                   if doc.find("content", {"name": "snippet"}) else "")
        if url:
            docs.append({"title": title, "url": url, "snippet": snippet})

    HTTP_CACHE[cache_key] = docs
    return docs

def fetch_medlineplus_page(url: str) -> Dict:
    """
    Fetch and extract main readable text from a MedlinePlus page.
    """
    cache_key = f"mplus_page::{url}"
    if cache_key in HTTP_CACHE:
        return HTTP_CACHE[cache_key]

    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    html = r.text

    soup = BeautifulSoup(html, "lxml")
    # MedlinePlus pages usually have a main article region; keep it robust.
    main = soup.find("main") or soup.find("article") or soup.body
    text = clean_text(main.get_text(" ", strip=True)) if main else clean_text(soup.get_text(" ", strip=True))

    result = {"url": url, "text": text}
    HTTP_CACHE[cache_key] = result
    return result
