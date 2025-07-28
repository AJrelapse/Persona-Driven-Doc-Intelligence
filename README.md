# Persona-Driven Document Intelligence

This project is a **generic intelligent document analysis system** that extracts and prioritizes the most relevant sections from multiple PDF documents based on a specific **persona** and their associated **job-to-be-done (JTBD)**.


---

## Problem Statement

In enterprise workflows, users like HR professionals, food bloggers, or travel planners often need to navigate through large amounts of PDF content to locate relevant information. This tool automatically extracts and ranks the most pertinent sections from 3–5 PDF documents based on:

- The **user persona** (e.g., HR professional, Travel Planner, Food Blogger)
- The **job-to-be-done** (e.g., "Plan a 4-day trip", "Create onboarding forms")

It supports fast and CPU-efficient processing under the following constraints:

- **Model size:** < 1GB  
- **Execution time:** ≤ 60 seconds for 3–5 documents  
- **Runs on:** CPU-only environment

---

## Features

- **PDF Section Extraction:** Identifies potential section titles and their corresponding content using PyMuPDF.
- **Semantic Relevance Ranking:** Uses `intfloat/e5-base-v2` model (Sentence Transformers) to score each section based on the persona's objective.
- **Persona-Specific Scoring Boosts:** Applies keyword-based boosting tailored to:
  - HR professionals
  - Food bloggers
  - Travel planners
- **Subsection Analysis:**
  - Extracts actionable instructions for HR tasks.
  - Parses ingredient + instruction lists for food personas.
  - Pulls coherent travel descriptions for itinerary planning.
- **Handles multiple PDF documents simultaneously.**

---

## Project Structure

```
    .
    ├── _pycache_  
    ├── collections  
    │   ├── Collection 1  
    │   │   ├── PDFs (Samples)
    │   │   └── challenge1b_input.json  
    │   ├── Collection 2  
    │   └── Collection 3  
    ├── output  
    ├── approach_explanation.md  
    ├── Dockerfile  
    ├── main.py  
    ├── requirements.txt  
    └── utils.py  
```

---

## Sample Input (`input.json`)

```json
{
  "persona": { "role": "Travel Planner" },
  "job_to_be_done": { "task": "Plan a trip of 4 days for a group of 10 college friends." },
  "documents": [
    { "filename": "South of France - Cities.pdf" },
    { "filename": "South of France - Cuisine.pdf" },
    { "filename": "South of France - Things to Do.pdf" }
  ]
}
```

---

## Execution Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/persona-doc-intelligence.git
cd persona-doc-intelligence
```

### 2. Set up environment (Optional: for manual run)

Ensure Python 3.8+ and pip are installed. Then:

```bash
pip install -r requirements.txt
```

Run the main script:

```bash
python main.py --input input.json --pdf_dir ./data
```

---

## Running via Docker

### 1. Build the image

```bash
docker build -t persona-doc-intelligence .
```

### 2. Run the container

```bash
docker run --rm -v $(pwd)/data:/app/data persona-doc-intelligence
```

> Make sure `input.json` is located at the root and PDFs are inside the `data/` directory.

---

## Model Used

- [`intfloat/e5-base-v2`](https://huggingface.co/intfloat/e5-base-v2) – An optimized Sentence Transformer model for semantic search.
- Pre-encoded input as:
  - `query: {persona_job}`
  - `passage: {section_text}`

---

## Hackathon Constraints Satisfied

- **Model size:** ~300MB
- **Inference speed:** ~10–15s for 5 documents
- **CPU-only**: No GPU dependencies
- **No external APIs used**: Fully self-contained
- **Sub-1GB image**: Lightweight Docker container

---

## Requirements

- Python 3.8+
- `PyMuPDF` (for PDF parsing)
- `sentence-transformers`
- `scikit-learn`
- `numpy`
- `re`, `os`, `datetime`, `collections`

These are already included in the Docker image.

---

## Sample Output (Snippet)

```json
{
  "extracted_sections": [
    {
      "document": "South of France - Cities.pdf",
      "section_title": "Comprehensive Guide to Major Cities in the South of France",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "South of France - Cuisine.pdf",
      "refined_text": "In addition to dining at top restaurants, there are several culinary experiences...",
      "page_number": 6
    }
  ]
}
```
---

## Author

**Ajay Anand**  
Feel free to fork, star, and raise issues!
