
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

# RAG-MBAN

Clinical information retrieval system built for structured evaluation and comparison.

This project compares two retrieval approaches:

- A direct, single-pass retrieval pipeline
- A structured, multi-step retrieval pipeline

Both systems retrieve medical information from MedlinePlus and generate answers using only retrieved content. Each run produces measurable evaluation metrics.

---

## Overview

The application:

- Accepts a clinical question
- Retrieves relevant medical pages
- Filters and ranks text segments
- Generates a structured answer
- Reports measurable system metrics

The system includes:

- Coverage scoring
- Token estimation
- Latency measurement
- Structured logging

---

## Features

- Side-by-side comparison of two retrieval strategies
- Transparent retrieval reasoning
- Keyword coverage scoring
- Token usage estimation
- Automatic run logging
- Web interface (FastAPI)
- Command-line compatibility

---

## Architecture

User Question
↓
Search MedlinePlus
↓
Fetch Pages
↓
Chunk + Filter
↓
Structured Answer Generation
↓
Metrics (Coverage, Tokens, Latency)


All answers are generated using retrieved context only.

---

## Evaluation Metrics

Each query produces:

- **Coverage (%)**  
  Percentage of key question terms found in retrieved content.

- **Token Estimate**  
  Approximate token count sent to the model.

- **Latency (seconds)**  
  End-to-end processing time.

Logs are automatically saved to:



data/logs/


---

## Setup

Requires Python 3.11+

### Install dependencies



uv sync


### Set environment variable

Create a `.env` file in the project root:



OPENAI_API_KEY=your_api_key_here


---

## Run the Application

Start the web interface:



uv run uvicorn app.ui:app --reload


Then open:



http://127.0.0.1:8000


---

## Example Queries

- bipolar disorder and insomnia
- borderline personality disorder
- major depressive disorder and generalized anxiety disorder
- diabetes and depression

---

## Project Structure



app/
core/
rag/
providers/
ui.py
data/
pyproject.toml
uv.lock


---

## Notes

- Runtime data and logs are excluded from version control.
- The system retrieves information exclusively from MedlinePlus.
- This project is intended for academic and evaluation purposes