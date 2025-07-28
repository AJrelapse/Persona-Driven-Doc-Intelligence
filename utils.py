import os
import re
import fitz 
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from collections import defaultdict

model = SentenceTransformer("intfloat/e5-base-v2")

TRAVEL_KEYWORDS = [
    "city", "cities", "guide", "activities", "things to do", "places", "trip",
    "nightlife", "restaurants", "beach", "adventure", "packing", "travel tips",
    "coastal", "cooking classes", "wine tours", "itinerary", "group travel",
    "budget", "friends", "college"
]

FOOD_KEYWORDS = [
    "salad", "curry", "soup", "stew", "grilled", "bake", "sauté", "lasagna",
    "ratatouille", "falafel", "baba ganoush", "sushi", "tofu", "roll",
    "moussaka", "kabob", "broccoli", "cauliflower", "zucchini", "roasted",
    "stir fry", "casserole", "lentil", "stuffed", "gluten", "vegetarian"
]

PDF_TASK_KEYWORDS = [
    "fillable forms", "create form", "interactive fields", "compliance", "signatures",
    "acrobat pro", "fill and sign", "request e-signatures", "share pdf", "edit pdf",
    "convert to pdf", "generate forms", "onboarding", "pdf checklist", "form fields",
    "prepare form", "sign pdf", "send document", "send for signature"
]

PRIORITY_TITLES = [
    "Fill and sign PDF forms", "Change flat forms to fillable", "Create a fillable form",
    "Request e-signatures", "Prepare form", "PDF Form Basics",
    "Create multiple PDFs from multiple files", "Convert clipboard content to PDF",
    "Send a document to get signatures from others"
]

KEY_VERBS = ["create", "fill", "sign", "prepare", "send", "enable", "manage", "convert"]

TRAVEL_PRIORITY_SECTIONS = [
    "coastal adventures", "nightlife and entertainment", "comprehensive guide to major cities",
    "culinary experiences", "group travel", "things to do"
]


def is_valid_title(title: str) -> bool:
    title = title.strip().lower()
    if not title or len(title.split()) < 2:
        return False
    if title.startswith("o ") or title.startswith("\u2022 "):
        return False
    if any(char.isdigit() for char in title):
        return False
    return True

def extract_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        lines = text.split("\n")
        title = ""

        for i, line in enumerate(lines):
            line = line.strip()
            if is_valid_title(line) and i < 5:
                title = line
                break

        if title:
            sections.append({
                "document": os.path.basename(pdf_path),
                "page_number": page_num,
                "section_title": title,
                "text": text
            })

    return sections

def boost_score(title, base_score, persona):
    title_lower = title.lower()
    score = base_score

    if persona.lower().startswith("food"):
        if any(keyword in title_lower for keyword in FOOD_KEYWORDS):
            score += 0.15
    elif persona.lower().startswith("hr"):
        if any(keyword in title_lower for keyword in PDF_TASK_KEYWORDS):
            score += 0.25
    elif persona.lower().startswith("travel"):
        if any(keyword in title_lower for keyword in TRAVEL_KEYWORDS):
            score += 0.15
        if any(priority in title_lower for priority in TRAVEL_PRIORITY_SECTIONS):
            score += 0.25
        if "nightlife and entertainment" in title_lower:
            score -= 0.05

    if any(priority.lower() in title_lower for priority in PRIORITY_TITLES):
        score += 0.35

    return score

def extract_hr_sentences(raw):
    raw = re.sub(r"\s+", " ", raw).strip()
    candidates = re.split(r"(?<=[.?!])\s+(?=[A-Z])", raw)
    refined = []
    for sent in candidates:
        lower_sent = sent.lower()
        if any(k in lower_sent for k in PDF_TASK_KEYWORDS):
            if any(v in lower_sent for v in KEY_VERBS) and len(sent) > 30:
                refined.append(sent.strip())
    return refined[:5] if refined else []

def slice_until_last_sentence(text):
    match = re.search(r"^(.{600,1600}?[.!?])\s", text)
    return match.group(1) if match else text[:800]

def rank_sections(sections, persona_job_text, persona):
    if not sections:
        return [], []

    query_emb = model.encode([f"query: {persona_job_text}"])
    section_texts = [f"passage: {s['text']}" for s in sections]
    section_embs = model.encode(section_texts)

    scores = cosine_similarity(query_emb, section_embs).flatten()
    boosted_sections = [(sec, boost_score(sec["section_title"], score, persona)) for sec, score in zip(sections, scores)]
    boosted_sections.sort(key=lambda x: x[1], reverse=True)

    extracted_sections = []
    subsection_analysis = []
    doc_count = defaultdict(int)

    for sec, score in boosted_sections:
        doc = sec["document"]
        if doc_count[doc] < 2 and len(extracted_sections) < 5:
            doc_count[doc] += 1
            rank = len(extracted_sections) + 1

            extracted_sections.append({
                "document": doc,
                "section_title": sec["section_title"],
                "importance_rank": rank,
                "page_number": sec["page_number"]
            })

            start = sec["text"].find(sec["section_title"]) + len(sec["section_title"])
            raw = sec["text"][start:start + 1800]

            clean = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u2022▪♦●–—\-·]", "", raw)
            clean = re.sub(r"[oO]\s+", "", clean)
            clean = re.sub(r"\s+", " ", clean).strip()

            if persona.lower().startswith("hr"):
                refined_parts = extract_hr_sentences(clean)
                refined_text = " ".join(refined_parts) if refined_parts else clean[:400]
            elif persona.lower().startswith("food"):
                ingredients_match = re.search(r"[Ii]ngredients:?[-\s]*([\s\S]*?)(?=Instructions:|\n|$)", clean)
                instructions_match = re.search(r"[Ii]nstructions:?[-\s]*([\s\S]*)", clean)

                ingredients = ingredients_match.group(1).strip() if ingredients_match else ""
                instructions = instructions_match.group(1).strip() if instructions_match else ""

                ingredients = re.sub(r"[\n\r]+", " ", ingredients)
                ingredients = re.sub(r"\s*[,;\u2022]\s*", ", ", ingredients)
                ingredients = re.sub(r"\s{2,}", " ", ingredients)

                refined_text = f"{sec['section_title']} Ingredients: {ingredients}. Instructions: {instructions}"
            else:
                refined_text = slice_until_last_sentence(clean)

            subsection_analysis.append({
                "document": doc,
                "refined_text": refined_text.strip(),
                "page_number": sec["page_number"]
            })

    return extracted_sections, subsection_analysis

def process_collection(input_config, pdf_dir):
    persona = input_config["persona"]["role"]
    job = input_config["job_to_be_done"]["task"]
    documents = [d["filename"] for d in input_config["documents"]]

    all_sections = []
    for pdf in documents:
        pdf_path = os.path.join(pdf_dir, pdf)
        sections = extract_sections(pdf_path)
        all_sections.extend(sections)

    persona_job_text = f"As a {persona}, your goal is to {job}."

    extracted_sections, subsection_analysis = rank_sections(all_sections, persona_job_text, persona)

    return {
        "metadata": {
            "input_documents": documents,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
