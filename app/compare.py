from app.rag.vanilla import run_vanilla_rag
from app.rag.agentic import run_agentic_rag


def compare(question: str):

    print("\n" + "="*80)
    print("RAG COMPARISON REPORT")
    print("="*80)

    v = run_vanilla_rag(question)
    a = run_agentic_rag(question)

    print("\nVANILLA:")
    print(f"Sources: {len(v.get('retrieved_sources', []))}")
    print(f"Answer length: {len(v.get('answer',''))}")

    print("\nAGENTIC:")
    print(f"Sources: {len(a.get('topic_urls', []))}")
    print(f"Answer length: {len(a.get('answer',''))}")

    print("\nConclusion:")
    if len(a.get("topic_urls", [])) > len(v.get("retrieved_sources", [])):
        print("Agentic demonstrated superior retrieval coverage.")
    else:
        print("Vanilla performed similarly.")
