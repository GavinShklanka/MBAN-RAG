from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
import re


# -------------------------------------------------------
# Basic Utilities
# -------------------------------------------------------

def estimate_tokens(text: str) -> int:
    # cheap heuristic: ~4 chars/token average in English
    return max(1, len(text) // 4)


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def extract_keywords(question: str) -> List[str]:
    """
    Dynamically extract meaningful keywords from the user question.
    Removes stopwords and short words.
    """
    stopwords = {
        "what", "should", "i", "if", "have", "how", "are",
        "the", "and", "is", "a", "an", "do", "does",
        "treated", "treatment", "manage", "management",
        "with", "for", "of", "to"
    }

    words = re.findall(r"\b[a-zA-Z]+\b", question.lower())

    keywords = [
        w for w in words
        if w not in stopwords and len(w) > 4
    ]

    # remove duplicates while preserving order
    seen = set()
    unique = []
    for w in keywords:
        if w not in seen:
            unique.append(w)
            seen.add(w)

    return unique


# -------------------------------------------------------
# Retrieval Data Structures
# -------------------------------------------------------

@dataclass
class RetrievalItem:
    source_url: str
    text: str


# -------------------------------------------------------
# Chunk Scoring & Filtering
# -------------------------------------------------------

def keyword_coverage(items: List[RetrievalItem], keywords: List[str]) -> Dict[str, bool]:
    joined = normalize(" ".join([it.text for it in items]))
    return {k: (normalize(k) in joined) for k in keywords}


def score_chunk(text: str, query_terms: List[str]) -> int:
    t = normalize(text)
    score = 0

    for term in query_terms:
        term_n = normalize(term)
        if term_n and term_n in t:
            score += 2

    # small density bonus
    if len(text) < 1200:
        score += 1

    return score


def filter_chunks(
    chunks: List[Tuple[str, Dict]],
    query_terms: List[str],
    max_keep: int,
    min_score: int = 2
) -> List[Tuple[str, Dict]]:

    scored = []

    for c, m in chunks:
        s = score_chunk(c, query_terms)
        if s >= min_score:
            scored.append((s, c, m))

    scored.sort(key=lambda x: x[0], reverse=True)

    kept = [(c, m) for _, c, m in scored[:max_keep]]
    return kept


# -------------------------------------------------------
# Retrieval Report
# -------------------------------------------------------
def print_retrieval_report(
    title: str,
    topic_urls: List[str],
    retrieved: List[RetrievalItem],
    context_sent: str,
    question: str
):

    print("\n" + "=" * 80)
    print(f"{title} — SYSTEM WALKTHROUGH")
    print("=" * 80)

    # ---------------------------------------------------
    # 01 Intent Analysis
    # ---------------------------------------------------

    print("\n01  Intent Analysis")
    print("User query interpreted as clinical retrieval task.")
    print(f"Raw Question: {question}")

    dynamic_keywords = extract_keywords(question)

    print("\nExtracted Keywords:")
    if dynamic_keywords:
        for k in dynamic_keywords:
            print(f"• {k}")
    else:
        print("No keywords extracted.")

    # ---------------------------------------------------
    # 02 Source Selection
    # ---------------------------------------------------

    print("\n02  Source Selection")
    if topic_urls:
        for u in topic_urls:
            print(f"• {u}")
    else:
        print("No sources selected.")

    # ---------------------------------------------------
    # 03 Context Reduction
    # ---------------------------------------------------

    print("\n03  Context Reduction")
    print(f"Chunks retained: {len(retrieved)}")

    # ---------------------------------------------------
    # 04 Coverage Evaluation (Dynamic + Scored)
    # ---------------------------------------------------

    print("\n04  Coverage Evaluation")

    if retrieved and dynamic_keywords:

        coverage = keyword_coverage(retrieved, dynamic_keywords)

        hits = sum(1 for v in coverage.values() if v)
        total = len(coverage)

        for k, found in coverage.items():
            print(f"{'✓' if found else '✗'} {k}")

        coverage_ratio = hits / total if total > 0 else 0
        coverage_percent = round(coverage_ratio * 100)

        print(f"\nCoverage Score: {coverage_percent}%")

    else:
        print("No retrieval content available for coverage evaluation.")
        coverage_percent = 0

    # ---------------------------------------------------
    # 05 Evidence Density
    # ---------------------------------------------------

    print("\n05  Evidence Density")
    print(f"Sources selected: {len(topic_urls)}")
    print(f"Chunks used: {len(retrieved)}")

    # ---------------------------------------------------
    # 06 Token Budget
    # ---------------------------------------------------

    approx_tokens = estimate_tokens(context_sent)

    print("\n06  Context Budget")
    print(f"Estimated tokens sent to LLM: ~{approx_tokens}")

    print("=" * 80)

    # -------------------------------------------------------
# Structured Metrics (UI + Logging)
# -------------------------------------------------------

def compute_metrics(
    retrieved: List[RetrievalItem],
    context_sent: str,
    question: str
) -> Dict:

    dynamic_keywords = extract_keywords(question)

    if retrieved and dynamic_keywords:
        coverage_dict = keyword_coverage(retrieved, dynamic_keywords)
        hits = sum(1 for v in coverage_dict.values() if v)
        total = len(coverage_dict)
        coverage_ratio = hits / total if total > 0 else 0.0
    else:
        coverage_ratio = 0.0

    approx_tokens = estimate_tokens(context_sent)

    return {
        "coverage": coverage_ratio,
        "tokens": approx_tokens
    }
