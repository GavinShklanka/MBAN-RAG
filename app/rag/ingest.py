from typing import List, Dict, Tuple
from app.core.text import simple_chunk
from app.rag.medlineplus_client import fetch_medlineplus_page

def ingest_pages(urls: List[str], max_pages: int = 5) -> List[Tuple[str, Dict]]:
    docs = []
    for url in urls[:max_pages]:
        page = fetch_medlineplus_page(url)
        docs.append((page["text"], {"source_url": url}))
    return docs

def chunk_docs(docs: List[Tuple[str, Dict]], max_chunks: int = 40) -> Tuple[List[str], List[Dict]]:
    all_chunks = []
    all_meta = []
    for text, meta in docs:
        chunks = simple_chunk(text, chunk_size=900, overlap=150)
        for c in chunks:
            all_chunks.append(c)
            all_meta.append(meta)
            if len(all_chunks) >= max_chunks:
                return all_chunks, all_meta
    return all_chunks, all_meta
