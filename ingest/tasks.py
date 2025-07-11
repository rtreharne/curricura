# ingest/tasks.py
from celery import shared_task
import csv
from io import TextIOWrapper
from .models import TranscriptUpload
from .utils import deidentify_text
#from core.utils import generate_embedding  
import time
import os

@shared_task
def add(x, y):
    return x + y


@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def process_transcript(self, transcript_id):
    try:
        transcript = TranscriptUpload.objects.get(id=transcript_id)

        # Wait for file to exist (sometimes needed in async upload)
        attempts = 0
        while not os.path.exists(transcript.file.path) and attempts < 5:
            time.sleep(1)
            attempts += 1

        with transcript.file.open("rb") as f:
            reader = csv.DictReader(TextIOWrapper(f, encoding="utf-8"), delimiter="\t")
            cleaned_lines = []

            for i, row in enumerate(reader):
                # Only deidentify the `transcript_text` column
                original_text = row.get("transcript_text", "")
                cleaned_text = deidentify_text(original_text)
                row["transcript_text"] = cleaned_text
                cleaned_lines.append(row)

                if i < 3:  # Print first 3 for debug
                    print(f"[DEBUG] Row {i} cleaned:")
                    print(f"  Before: {original_text}")
                    print(f"  After : {cleaned_text}")

        # Reassemble TSV as cleaned_text
        if cleaned_lines:
            output = TextIOWrapper(open(os.devnull, 'w'))  # dummy file
            headers = cleaned_lines[0].keys()
            from io import StringIO
            output_buffer = StringIO()
            writer = csv.DictWriter(output_buffer, fieldnames=headers, delimiter="\t")
            writer.writeheader()
            writer.writerows(cleaned_lines)
            cleaned_text = output_buffer.getvalue()
        else:
            cleaned_text = ""

        transcript.cleaned_text = cleaned_text
        transcript.save()

    except TranscriptUpload.DoesNotExist:
        print(f"[ERROR] Transcript ID {transcript_id} not found.")
        raise self.retry(exc=Exception("Transcript not found."))

    except Exception as e:
        print(f"[ERROR] Unexpected error for ID {transcript_id}: {e}")
        raise self.retry(exc=e)

