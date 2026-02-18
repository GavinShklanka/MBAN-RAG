from typing import Dict, List

from langchain_openai import ChatOpenAI
from app.core.eval import extract_keywords
from app.rag.medlineplus_client import fetch_medlineplus_page
from app.core.config import settings
from app.core.safety import SAFETY_PREAMBLE
from app.core.eval import RetrievalItem, print_retrieval_report, filter_chunks
from app.rag.medlineplus_client import medlineplus_search, fetch_medlineplus_page
from app.core.text import simple_chunk
from app.core.eval import compute_metrics

def run_agentic_rag(
    question: str,
    location: str = "",
    max_topics: int = 5,
    max_pages: int = 5,
    max_chunks: int = 20,
    max_context_chunks: int = 8,
) -> Dict:

    # ----------------------------
    # 1️⃣ Query Decomposition
    # ----------------------------

    def decompose(q: str) -> List[str]:
        base = q.strip().lower()
        subs = []

        keywords = extract_keywords(q)

        for k in keywords:
            subs.append(f"{k} MedlinePlus")

        subs.append(q)

        seen = set()
        unique = []

        for s in subs:
            if s not in seen:
                unique.append(s)
                seen.add(s)

        return unique

    subqs = decompose(question)

    # ----------------------------
    # 2️⃣ Retrieval Loop
    # ----------------------------

    selected_urls: List[str] = []
    fetched_pages: List[Dict] = []

    for sq in subqs:
        if len(selected_urls) >= max_pages:
            break

        topics = medlineplus_search(sq, max_topics=max_topics)

        for t in topics:
            url = t.get("url")
            if url and url not in selected_urls:
                selected_urls.append(url)

            if len(selected_urls) >= max_pages:
                break

    # ----------------------------
    # 3️⃣ Fetch Pages
    # ----------------------------

    for url in selected_urls[:max_pages]:
        page = fetch_medlineplus_page(url)
        text = page["text"][:9000]

        fetched_pages.append({
            "url": url,
            "text": text
        })

    # ----------------------------
    # 4️⃣ Chunking
    # ----------------------------

    all_chunks = []
    all_meta = []

    for p in fetched_pages:
        chunks = simple_chunk(p["text"], chunk_size=900, overlap=150)

        for c in chunks:
            all_chunks.append(c)
            all_meta.append({"source_url": p["url"]})

            if len(all_chunks) >= max_chunks:
                break

        if len(all_chunks) >= max_chunks:
            break

    # ----------------------------
    # 5️⃣ Filtering
    # ----------------------------

    query_terms = [w for w in question.split() if len(w) > 4]

    filtered = filter_chunks(
        list(zip(all_chunks, all_meta)),
        query_terms=query_terms,
        max_keep=max_context_chunks,
    )

    retrieved_items = [
        RetrievalItem(source_url=m["source_url"], text=c)
        for c, m in filtered
    ]

    context = "\n\n".join([c for c, _ in filtered])

    # ----------------------------
    # 6️⃣ Evaluation Report
    # ----------------------------

    print_retrieval_report(
        "AGENTIC RAG",
        topic_urls=selected_urls,
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
    # 7️⃣ LLM Answer
    # ----------------------------

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    final_prompt = (
        f"{SAFETY_PREAMBLE}\n\n"
        "Use ONLY the MedlinePlus context below.\n"
        "Return a structured answer with:\n"
        "- Key points relevant to the question\n"
        "- Practical next steps\n"
        "- When to seek urgent care\n"
        "- Sources (list URLs)\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{context}\n\n"
        f"Sources:\n" + "\n".join(selected_urls) + "\n\n"
        "Answer:"
    )

    answer = llm.invoke(final_prompt).content

    return {
        "answer": answer,
        "coverage": metrics["coverage"],
        "tokens": metrics["tokens"]
    }
