from openai import OpenAI
from ingest.models import TranscriptChunk
from pgvector.django import CosineDistance
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_top_chunks(query, top_n=100):
    # Embed the query using OpenAI
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_vec = response.data[0].embedding

    # Query using pgvector similarity (lower = more similar)
    chunks = (
        TranscriptChunk.objects
        .exclude(embedding__isnull=True)
        .annotate(similarity=CosineDistance("embedding", query_vec))
        .order_by("similarity")[:top_n]
    )

    # Return tuples of (similarity score, chunk) for the template
    return [(chunk.similarity, chunk) for chunk in chunks]
