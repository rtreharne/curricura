from ingest.models import TranscriptChunk, CanvasChunk, YouTubeChunk
from pgvector.django import CosineDistance
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_top_chunks(query, top_n=100):
    # Embed the query
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_vec = response.data[0].embedding

    # Transcript chunks (Lecture Transcripts)
    transcript_chunks = (
        TranscriptChunk.objects
        .exclude(embedding__isnull=True)
        .annotate(similarity=CosineDistance("embedding", query_vec))
        .order_by("similarity")[:top_n]
    )

    # Canvas chunks
    canvas_chunks = (
        CanvasChunk.objects
        .exclude(embedding__isnull=True)
        .annotate(similarity=CosineDistance("embedding", query_vec))
        .order_by("similarity")[:top_n]
    )

    # YouTube chunks
    youtube_chunks = (
        YouTubeChunk.objects
        .exclude(embedding__isnull=True)
        .annotate(similarity=CosineDistance("embedding", query_vec))
        .order_by("similarity")[:top_n]
    )

    # Merge all results with source labels
    combined = (
        [(chunk.similarity, chunk, "transcript") for chunk in transcript_chunks] +
        [(chunk.similarity, chunk, "canvas") for chunk in canvas_chunks] +
        [(chunk.similarity, chunk, "youtube") for chunk in youtube_chunks]
    )

    combined.sort(key=lambda x: x[0])  # Sort by similarity score (lower = better)
    return combined[:top_n]


from ingest.models import CanvasFile, CanvasPage, CanvasAssignment

def resolve_canvas_parent(chunk):
    if chunk.parent_type == 'file':
        return CanvasFile.objects.filter(id=chunk.parent_id).first()
    elif chunk.parent_type == 'page':
        return CanvasPage.objects.filter(id=chunk.parent_id).first()
    elif chunk.parent_type == 'assignment':
        return CanvasAssignment.objects.filter(id=chunk.parent_id).first()
    return None
