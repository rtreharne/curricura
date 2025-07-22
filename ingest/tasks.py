# ingest/tasks.py
from celery import shared_task
import csv
from io import TextIOWrapper
import json
from .utils import save_canvas_object, chunk_text

import time
import os



from celery import shared_task
from .models import TranscriptChunk, VideoTranscript
from .utils import deidentify_text, generate_embedding
from django.utils.timezone import now
import zipfile

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

@shared_task
def process_canvas_json(raw_json, course_id):
    from .models import Course
    course = Course.objects.get(id=course_id)
    try:
        data = json.loads(raw_json)
        if isinstance(data, list):
            for item in data:
                save_canvas_object(item, course)
        elif isinstance(data, dict):
            save_canvas_object(data, course)
    except Exception as e:
        print(f"[ERROR] Failed to process JSON for course {course_id}: {e}")

@shared_task
def process_canvas_zip(zip_path, course_id):
    from .models import Course
    from .tasks import process_canvas_chunks

    course = Course.objects.get(id=course_id)

    if not os.path.exists(zip_path):
        print(f"[ERROR] ZIP path does not exist: {zip_path}")
        return

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            json_files = [f for f in zf.namelist() if f.endswith('.json')]
            print(f"[INFO] Found {len(json_files)} JSON files in {zip_path}")

            for filename in json_files:
                print(f"[INFO] Processing {filename}")
                try:
                    raw_data = zf.read(filename).decode('utf-8')
                    data = json.loads(raw_data)
                    if isinstance(data, list):
                        for item in data:
                            save_canvas_object(item, course)
                    elif isinstance(data, dict):
                        save_canvas_object(data, course)
                except Exception as e:
                    print(f"[ERROR] Failed to process {filename}: {e}")

        # Trigger chunk creation after all files are saved
        print(f"[INFO] Triggering Canvas chunking for course {course_id}...")
        process_canvas_chunks.delay(course_id)

    except Exception as e:
        print(f"[ERROR] Failed to open ZIP {zip_path}: {e}")
    finally:
        try:
            os.remove(zip_path)
        except OSError:
            pass



from .models import CanvasFile, CanvasPage, CanvasAssignment, CanvasChunk


@shared_task
def process_canvas_chunks(course_id=None):
    """
    Process all Canvas content into CanvasChunks with embeddings.
    If course_id is provided, only that course is processed.
    """
    from .models import CanvasFile, CanvasPage, CanvasAssignment, CanvasChunk
    from .utils import deidentify_text, generate_embedding, chunk_text

    print(f"[INFO] Starting Canvas chunking for course {course_id or 'ALL'}")

    files = CanvasFile.objects.all()
    pages = CanvasPage.objects.all()
    assignments = CanvasAssignment.objects.all()

    if course_id:
        files = files.filter(course_id=course_id)
        pages = pages.filter(course_id=course_id)
        assignments = assignments.filter(course_id=course_id)

    for f in files:
        create_chunks_for_object('file', f.id, f.text)
    for p in pages:
        create_chunks_for_object('page', p.id, p.text)
    for a in assignments:
        create_chunks_for_object('assignment', a.id, a.description)

    print("[INFO] Canvas chunking complete.")


@shared_task
def create_chunks_for_object(parent_type, parent_id, text):
    from .models import CanvasChunk
    from .utils import deidentify_text, generate_embedding

    if not text or not text.strip():
        return

    # Skip if already chunked
    if CanvasChunk.objects.filter(parent_type=parent_type, parent_id=parent_id).exists():
        print(f"[INFO] Skipping {parent_type} {parent_id}, already chunked.")
        return

    # Simple splitting into 500-character chunks (replace with token-based chunking if needed)
    chunk_size = 500
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    for chunk in chunks:
        try:
            cleaned = deidentify_text(chunk)
            embedding = generate_embedding(cleaned)[0]
            CanvasChunk.objects.create(
                parent_type=parent_type,
                parent_id=parent_id,
                text=chunk,
                cleaned_text=cleaned,
                embedding=embedding
            )
            print(f"[INFO] Created chunk for {parent_type} {parent_id}")
        except Exception as e:
            print(f"[ERROR] Failed to create chunk for {parent_type} {parent_id}: {e}")



from .models import YouTubeVideo, YouTubeChunk


@shared_task
def process_youtube_chunks(video_id, chunks):
    """
    Each element in `chunks` is a dict with:
    - 'text'
    - 'timestamp'
    """
    try:
        video = YouTubeVideo.objects.get(id=video_id)
    except YouTubeVideo.DoesNotExist:
        print(f"[ERROR] YouTubeVideo {video_id} not found.")
        return

    for i, chunk in enumerate(chunks):
        text = chunk['text'].strip()
        timestamp = chunk['timestamp']

        if len(text.split()) < 3:
            continue

        try:
            embedding = generate_embedding(text)[0]
            YouTubeChunk.objects.create(
                video=video,
                text=text,
                timestamp=timestamp,
                embedding=embedding
            )
            print(f"[INFO] Created chunk {i} for video {video_id} at {timestamp}")
        except Exception as e:
            print(f"[ERROR] Failed chunk {i} for video {video_id}: {e}")


from .helpers.youtube import fetch_youtube_data
from .models import YouTubeVideo, Course
from .utils import parse_transcript

@shared_task(rate_limit='6/m') 
def process_youtube(video_url, course_id):
    data = fetch_youtube_data(video_url)
    title = data['title']
    transcript = data['transcript']

    print("TRANSCRIPT", transcript)
    course = Course.objects.get(id=course_id)

    video = YouTubeVideo.objects.create(course=course, url=video_url, title=title)

    # Parse transcript into chunks
    raw_chunks = parse_transcript(transcript, chunk_word_limit=200, overlap_ratio=0.1)
    chunk_data = [{'text': text, 'timestamp': timestamp} for timestamp, text in raw_chunks]

    # Queue async embedding
    process_youtube_chunks(video.id, chunk_data)
