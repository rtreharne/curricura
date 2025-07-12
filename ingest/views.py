from django.shortcuts import render, redirect
from ingest.tasks import process_transcript
from django.db import transaction
import csv
from datetime import datetime
from .models import VideoTranscript

import logging
logger = logging.getLogger(__name__)

from .forms import TranscriptTSVUploadForm

def upload_transcript_tsv(request):
    if request.method == 'POST':
        form = TranscriptTSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            tsv_file = request.FILES['tsv_file']
            selected_year = int(form.cleaned_data['year'])

            decoded = tsv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded, delimiter='\t')

            from collections import defaultdict
            grouped = defaultdict(list)
            for row in reader:
                video_url = row['video_url'].strip()
                grouped[video_url].append({
                    'transcript_url': row['transcript_url'].strip(),
                    'transcript_text': row['transcript_text'].strip(),
                    'transcript_timestamp': row['transcript_timestamp'].strip(),
                    'date': row['date'].strip(),
                    'time': row['time'].strip(),
                })



            for url, rows in grouped.items():
                print(url, rows)
                try:
                    dt = datetime.strptime(f"{rows[0]['date']} {rows[0]['time']}", "%m/%d/%Y %I:%M %p")
                except Exception as e:
                    print(f"[ERROR] Failed to parse datetime for {url}: {e}")
                    continue

                vt = VideoTranscript.objects.create(
                    url=url,
                    datetime=dt,
                    year=selected_year
                )

                task_rows = [
                    {
                        'text': r['transcript_text'],
                        'transcript_url': r['transcript_url'],
                        'transcript_timestamp': r['transcript_timestamp']
                    }
                    for r in rows
                ]
                process_transcript.delay(vt.id, task_rows)

            return redirect('upload_success')

    else:
        form = TranscriptTSVUploadForm()

    return render(request, 'ingest/upload.html', {'form': form})



def upload_success(request):
    return render(request, 'ingest/success.html')

