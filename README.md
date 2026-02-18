# Vanilla RAG vs Agentic RAG (MedlinePlus)

This project implements two systems for healthcare information retrieval:
1) Vanilla RAG: search → fetch → chunk → embed → retrieve → generate
2) Agentic RAG: an agent that decides what to search/fetch/index/retrieve using tools

Primary medical information source: MedlinePlus (NLM/NIH).

## Requirements
- Python 3.11+
- uv installed

## Setup
1) Create environment:
   uv init
   uv add requests beautifulsoup4 lxml typer pydantic python-dotenv tiktoken diskcache chromadb langchain langchain-openai streamlit

2) Configure keys:
   Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

3) Run (CLI)
- Vanilla:
  uv run python -m app.cli vanilla --question "..." --location "Halifax, NS"
- Agentic:
  uv run python -m app.cli agentic --question "..." --location "Halifax, NS"

4) Run UI
  uv run streamlit run app/ui.py

## Budget Controls
Use `--max-topics`, `--max-pages`, `--max-chunks` to cap retrieval volume.
Embeddings and HTTP fetches are cached on disk under `data/`.

## Notes
- This app provides general information only and is not medical advice.
