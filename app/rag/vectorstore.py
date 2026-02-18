from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.core.config import settings
from app.core.cache import EMBED_CACHE
import hashlib
import os

PERSIST_DIR = "data/chroma"

def _hash_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()

class CachedEmbeddings(OpenAIEmbeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        out = []
        missing = []
        missing_idx = []
        for i, t in enumerate(texts):
            k = f"emb::{settings.openai_embed_model}::{_hash_text(t)}"
            if k in EMBED_CACHE:
                out.append(EMBED_CACHE[k])
            else:
                out.append(None)
                missing.append(t)
                missing_idx.append(i)

        if missing:
            computed = super().embed_documents(missing)
            for idx, vec in zip(missing_idx, computed):
                t = texts[idx]
                k = f"emb::{settings.openai_embed_model}::{_hash_text(t)}"
                EMBED_CACHE[k] = vec
                out[idx] = vec
        return out

def get_store(collection: str = "mplus") -> Chroma:
    os.makedirs(PERSIST_DIR, exist_ok=True)
    emb = CachedEmbeddings(model=settings.openai_embed_model, api_key=settings.openai_api_key)
    return Chroma(collection_name=collection, embedding_function=emb, persist_directory=PERSIST_DIR)

def add_texts(store: Chroma, chunks: List[str], metadatas: List[Dict]) -> None:
    store.add_texts(texts=chunks, metadatas=metadatas)
    store.persist()
