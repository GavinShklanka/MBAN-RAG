from typing import Dict, List

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.safety import SAFETY_PREAMBLE
from app.core.eval import (
    RetrievalItem,
    filter_chunks,
    print_retrieval_report,
    compute_metrics
)

from app.rag.medlineplus_client import (
    medlineplus_search,
    fetch_medlineplus_page
)

from app.core.text import simple_chunk


def run_vanilla_rag(
    question: str,
    max_topics: int = 5,
    max_pages: int = 5,
    max_chunks: int = 20,
    max_context_chunks: int = 8,
) -> Dict:

    # ----------------------------
    # 1️⃣ Search
    # ----------------------------

    topics = medlineplus_search(question, max_topics=max_topics)
    urls = [t["url"] for t in topics if t.get("url")][:max_pages]

    # ----------------------------
    # 2️⃣ Fetch Pages
    # ----------------------------

    pages = []
    for u in urls:
        page = fetch_medlineplus_page(u)
        pages.append({"url": u, "text": page["text"][:9000]})

    # ----------------------------
    # 3️⃣ Chunking
    # ----------------------------

    all_chunks = []
    all_meta = []

    for p in pages:
        for c in simple_chunk(p["text"], chunk_size=900, overlap=150):
            all_chunks.append(c)
            all_meta.append({"source_url": p["url"]})

            if len(all_chunks) >= max_chunks:
                break

        if len(all_chunks) >= max_chunks:
            break

    # ----------------------------
    # 4️⃣ Filtering
    # ----------------------------

    query_terms = [w for w in question.split() if len(w) > 4]

    filtered = filter_chunks(
        list(zip(all_chunks, all_meta)),
        query_terms=query_terms,
        max_keep=max_context_chunks
    )

    retrieved_items = [
        RetrievalItem(source_url=m["source_url"], text=c)
        for c, m in filtered
    ]

    context = "\n\n".join([c for c, _ in filtered])

    # ----------------------------
    # 5️⃣ Evaluation Report
    # ----------------------------

    print_retrieval_report(
        "VANILLA RAG",
        topic_urls=urls,
        retrieved=retrieved_items,
        context_sent=context,
        question=question
    )

    metrics = compute_metrics(
        retrieved=retrieved_items,
        context_sent=context,
        question=question
    )

    # ----------------------------
    # 6️⃣ LLM Answer
    # ----------------------------

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0
    )

    prompt = (
        f"{SAFETY_PREAMBLE}\n\n"
        "Use ONLY the context below.\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{context}\n\n"
        "Answer:"
    )

    answer = llm.invoke(prompt).content

    return {
        "answer": answer,
        "coverage": metrics["coverage"],
        "tokens": metrics["tokens"]
    }
