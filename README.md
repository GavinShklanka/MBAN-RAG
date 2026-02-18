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

