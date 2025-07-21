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

from django.db import IntegrityError

def save_canvas_object(data, course):
    try:
        if 'filename' in data and 'canvas_file_id' in data:
            raw_text = data.get('text', '')
            cleaned = deidentify_text(raw_text)
            CanvasFile.objects.update_or_create(
                course=course,
                canvas_file_id=data.get('canvas_file_id'),
                defaults={
                    'filename': data.get('filename'),
                    'file_url': data.get('file_url'),
                    'text': raw_text,
                    'cleaned_text': cleaned
                }
            )

        elif 'title' in data and 'canvas_course_id' in data:
            raw_text = data.get('text', '')
            cleaned = deidentify_text(raw_text)
            CanvasPage.objects.update_or_create(
                url=data.get('url'),
                defaults={
                    'course': course,
                    'title': data.get('title'),
                    'canvas_course_id': data.get('canvas_course_id'),
                    'text': raw_text,
                    'cleaned_text': cleaned
                }
            )

        elif 'id' in data and 'course_id' in data and 'name' in data:
            raw_description = data.get('description', '')
            cleaned_desc = deidentify_text(raw_description)
            CanvasAssignment.objects.update_or_create(
                assignment_id=data.get('id'),
                canvas_course_id=data.get('course_id'),
                defaults={
                    'course': course,
                    'name': data.get('name'),
                    'html_url': data.get('html_url'),
                    'description': raw_description,
                    'cleaned_description': cleaned_desc,
                    'points_possible': data.get('points_possible', 0.0),
                    'due_at': data.get('due_at'),
                    'created_at_canvas': data.get('created_at'),
                    'updated_at_canvas': data.get('updated_at'),
                    'submission_types': data.get('submission_types', []),
                    'external_tool_url': data.get('external_tool_tag_attributes', {}).get('url'),
                    'full_json': data
                }
            )
    except IntegrityError as e:
        print(f"[WARNING] Duplicate detected for Canvas object: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to save Canvas object: {e}")

def chunk_text(text, max_tokens=300, overlap=50):
    words = text.split()
    start = 0
    while start < len(words):
        end = start + max_tokens
        chunk = " ".join(words[start:end])
        yield chunk
        start += max_tokens - overlap


import re

import re

def parse_transcript(transcript_text, chunk_word_limit=100, overlap_ratio=0.1):
    """
    Parses a raw transcript into ~200-word chunks with overlap.
    Only the first timestamp of each chunk is kept.
    - transcript_text: raw transcript text with timestamps and lines.
    - chunk_word_limit: maximum number of words per chunk (default 200).
    - overlap_ratio: fraction of overlap between consecutive chunks (default 10%).
    """
    # Split lines and identify timestamps
    lines = transcript_text.splitlines()
    timestamp_pattern = re.compile(r'^\d{1,2}:\d{2}(?::\d{2})?$')

    entries = []
    current_timestamp = "0:00"
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if timestamp_pattern.match(line):
            current_timestamp = line
        else:
            entries.append((current_timestamp, line))

    if not entries:
        return []

    # Flatten entries into individual words while keeping timestamps
    flat_entries = []
    for ts, text in entries:
        for word in text.split():
            flat_entries.append((ts, word))

    chunks = []
    overlap_words = int(chunk_word_limit * overlap_ratio)
    start = 0
    total_words = len(flat_entries)

    while start < total_words:
        end = min(total_words, start + chunk_word_limit)
        chunk_words = [w for _, w in flat_entries[start:end]]
        first_timestamp = flat_entries[start][0]
        chunks.append((first_timestamp, " ".join(chunk_words)))
        start += chunk_word_limit - overlap_words  # move window with overlap

    return chunks

