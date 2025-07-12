from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ingest.models import TranscriptUpload
from ingest.utils import generate_embedding

def search_transcripts(query, top_k=5):
    """
    Returns top-k TranscriptUpload objects most similar to the query.
    """
    query_embedding = generate_embedding(query)[0]  # assume single chunk
    query_vector = np.array(query_embedding).reshape(1, -1)

    results = []
    for transcript in TranscriptUpload.objects.exclude(embedding=None):
        try:
            transcript_vectors = np.array(transcript.embedding)
            if transcript_vectors.ndim == 1:
                transcript_vectors = transcript_vectors.reshape(1, -1)
            sim = cosine_similarity(query_vector, transcript_vectors).max()
            results.append((sim, transcript))
        except Exception as e:
            print(f"[ERROR] Comparing with transcript {transcript.id}: {e}")

    results.sort(reverse=True, key=lambda x: x[0])
    return results[:top_k]
