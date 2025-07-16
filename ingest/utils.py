import re
import spacy
import os
from openai import OpenAI
from .models import CanvasFile, CanvasPage, CanvasAssignment

# Load spaCy model and raise max length
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 20_000_000

def deidentify_text(text, chunk_size=100000):
    """
    Replaces personal and sensitive info using spaCy NER and regex fallback.
    Logs matches as they are found (before replacement).
    """
    spans = []

    # === Step 1: Chunk + NER ===
    start_idx = 0
    while start_idx < len(text):
        chunk = text[start_idx : start_idx + chunk_size]
        doc = nlp(chunk)
        for ent in doc.ents:
            label = None
            if ent.label_ == "PERSON":
                label = "[NAME]"
            elif ent.label_ == "EMAIL":
                label = "[EMAIL]"
        
            if label:
                global_start = start_idx + ent.start_char
                global_end = start_idx + ent.end_char
                spans.append((global_start, global_end, label))
                print(f"NER match: '{ent.text}' → {label}")
        start_idx += chunk_size

    spans.sort()
    final_spans = []
    last_end = -1
    for start, end, label in spans:
        if start >= last_end:
            final_spans.append((start, end, label))
            last_end = end

    for start, end, label in reversed(final_spans):
        text = text[:start] + label + text[end:]

    return text

import tiktoken

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ENCODING = tiktoken.encoding_for_model("text-embedding-3-small")
MAX_TOKENS = 8000

def tokenize(text):
    return ENCODING.encode(text)

def detokenize(tokens):
    return ENCODING.decode(tokens)

def generate_embedding(text, max_tokens=8000):
    """
    Token-aware embedding generator that chunks text safely under token limits.
    Returns a list of embedding vectors.
    """
    tokens = tokenize(text)
    chunks = [
        tokens[i:i + max_tokens]
        for i in range(0, len(tokens), max_tokens)
    ]

    embeddings = []
    for i, token_chunk in enumerate(chunks):
        try:
            chunk_text = detokenize(token_chunk)
            response = client.embeddings.create(
                input=chunk_text,
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
        except Exception as e:
            print(f"[WARNING] Failed to embed chunk {i}: {e}")

    return embeddings

def save_canvas_object(data, course):
    if 'filename' in data and 'canvas_file_id' in data:
        CanvasFile.objects.create(
            course=course,
            filename=data.get('filename'),
            canvas_file_id=data.get('canvas_file_id'),
            text=data.get('text', '')
        )
    elif 'title' in data and 'canvas_course_id' in data:
        CanvasPage.objects.create(
            course=course,
            title=data.get('title'),
            url=data.get('url'),
            canvas_course_id=data.get('canvas_course_id'),
            text=data.get('text', '')
        )
    elif 'id' in data and 'course_id' in data and 'name' in data:
        CanvasAssignment.objects.create(
            course=course,
            assignment_id=data.get('id'),
            course_id=data.get('course_id'),
            name=data.get('name'),
            html_url=data.get('html_url'),
            description=data.get('description', ''),
            points_possible=data.get('points_possible', 0.0),
            due_at=data.get('due_at'),
            created_at_canvas=data.get('created_at'),
            updated_at_canvas=data.get('updated_at'),
            submission_types=data.get('submission_types', []),
            external_tool_url=data.get('external_tool_tag_attributes', {}).get('url'),
            full_json=data
        )
