# ingest/tasks.py
from celery import shared_task
import csv
from io import TextIOWrapper

import time
import os



from celery import shared_task
from .models import TranscriptChunk, VideoTranscript
from .utils import deidentify_text, generate_embedding
from django.utils.timezone import now


@shared_task
def process_transcript(transcript_id, rows):
    """
    Each row should be a dict with keys:
    - 'text': raw transcript text
    - 'timestamp': HH:MM:SS string
    """
    try:
        transcript = VideoTranscript.objects.get(id=transcript_id)
    except VideoTranscript.DoesNotExist:
        print(f"[ERROR] Transcript with ID {transcript_id} not found.")
        return

    for i, row in enumerate(rows):
        text = row['text'].strip()
        timestamp = row['transcript_timestamp'].strip()
        transcript_url = row['transcript_url']

        if len(text.split()) < 3:
            continue  # Skip trivial rows

        try:
            cleaned = deidentify_text(text)
            embedding = generate_embedding(cleaned)[0]  # single chunk

            TranscriptChunk.objects.create(
                transcript=transcript,
                text=text,
                cleaned_text=cleaned,
                timestamp=timestamp,
                embedding=embedding,
                transcript_url=transcript_url
            )
            print(f"[INFO] Created chunk {i} for transcript {transcript_id} at {timestamp}")

        except Exception as e:
            print(f"[ERROR] Failed to process chunk {i} for transcript {transcript_id}: {e}")

