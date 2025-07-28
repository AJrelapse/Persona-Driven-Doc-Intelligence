# Approach Explanation

## Overview

The solution is designed to address the challenge of extracting and prioritizing relevant information from a collection of documents based on a defined persona and a specific job-to-be-done. The system acts as an intelligent document analyst, working on CPU, using a lightweight transformer model, and completing the processing within 60 seconds for 3–5 documents.

---

## Methodology

### 1. Document Parsing

We use **PyMuPDF (`fitz`)** for parsing PDFs. For each document, the system reads every page and identifies section titles by scanning the first few lines of text. Titles are validated based on simple heuristics (length, formatting, presence of digits) to ensure quality section detection. Each valid section includes:
- Document name
- Page number
- Section title
- Full text of the page

---

### 2. Embedding and Relevance Scoring

For semantic understanding, we use the **`intfloat/e5-base-v2`** model from the `sentence-transformers` library. It is optimized for retrieval tasks, fast on CPU, and under 1GB in size.

A query is constructed from the persona and the job (e.g., _“As a Travel Planner, your goal is to Plan a 4-day trip…”_). Each section is embedded as a “passage” and cosine similarity scores are computed against the query embedding.

---

### 3. Heuristic Boosting

To align rankings better with the persona’s domain, we apply keyword-based boosting. Domain-specific keywords and priority section titles (e.g., “Create Fillable Form” for HR, “Culinary Experiences” for Food) are used to increase the relevance score. This hybrid method ensures generalization across diverse persona-job combinations without requiring fine-tuning.

---

### 4. Subsection Refinement

Top 5 relevant sections (max 2 per document) are selected and further refined:
- **HR Persona**: Filters informative sentences with verbs and task-related keywords.
- **Food Persona**: Extracts ingredients and instructions using pattern matching.
- **Others**: Extracts coherent paragraphs using sentence-aware truncation.

The goal is to deliver crisp and persona-relevant content in the `subsection_analysis` section.

---

## Output Structure

The final output JSON includes:
- `metadata`: Input documents, persona, job description, timestamp
- `extracted_sections`: Ranked section titles with page info
- `subsection_analysis`: Condensed relevant text per section

---

## Performance

- **Model**: `e5-base-v2` (<500MB)
- **No internet**: All dependencies are installed via Docker
- **CPU-only**: Optimized pipeline completes within 60 seconds

---

## Summary

This system combines transformer-based semantic search with domain-aware heuristics to provide fast, accurate, and persona-specific document analysis. The modular design ensures it can generalize across various domains while staying efficient and lightweight.
