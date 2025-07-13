import numpy as np
from openai import OpenAI
from ingest.models import TranscriptChunk
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def get_top_chunks(query, top_n=5):
    # Embed the query using OpenAI
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_vec = response.data[0].embedding

    # Compare with all chunks that have embeddings
    chunks = TranscriptChunk.objects.exclude(embedding__isnull=True)
    scored = []

    for chunk in chunks:
        try:
            score = cosine_similarity(query_vec, chunk.embedding)
            scored.append((score, chunk))
        except Exception:
            continue  # skip any problematic embeddings

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_n]
