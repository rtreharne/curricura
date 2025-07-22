
from .forms import TranscriptTSVUploadForm

from django.shortcuts import render, redirect
from .forms import TranscriptTSVUploadForm
from .models import VideoTranscript
from .tasks import process_transcript, process_canvas_json
from datetime import datetime
import csv
from collections import defaultdict
import json
from .utils import save_canvas_object

from collections import defaultdict
from datetime import datetime
import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import TranscriptTSVUploadForm
from .models import VideoTranscript
from .tasks import process_transcript  # assuming you have this task

@login_required
def upload_transcript_tsv(request):
    if request.method == 'POST':
        form = TranscriptTSVUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            tsv_file = request.FILES['tsv_file']
            course = form.cleaned_data['course']

            decoded = tsv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded, delimiter='\t')

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
                try:
                    dt = datetime.strptime(
                        f"{rows[0]['date']} {rows[0]['time']}", "%m/%d/%Y %I:%M %p"
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to parse datetime for {url}: {e}")
                    continue

                vt = VideoTranscript.objects.create(
                    url=url,
                    datetime=dt,
                    course=course,
                )

                task_rows = [
                    {
                        'text': r['transcript_text'],
                        'transcript_url': r['transcript_url'],
                        'transcript_timestamp': r['transcript_timestamp'],
                    }
                    for r in rows
                ]
                process_transcript.delay(vt.id, task_rows)

            return redirect('upload_success')
    else:
        form = TranscriptTSVUploadForm(user=request.user)

    return render(request, 'ingest/upload.html', {'form': form})




def upload_success(request):
    return render(request, 'ingest/success.html')


from .forms import CanvasJSONUploadForm
from .models import CanvasFile, CanvasPage, CanvasAssignment

import zipfile
import tempfile
from .tasks import process_canvas_zip
import os
import tempfile
import shutil

from django.conf import settings

@login_required
def upload_canvas_json(request):
    if request.method == 'POST':
        form = CanvasJSONUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            course = form.cleaned_data['course']
            zip_file = request.FILES['zip_file']
            tmp_filename = f"{course.id}_{zip_file.name}"
            tmp_path = os.path.join(settings.TMP_CANVAS_ZIP_DIR, tmp_filename)
            with open(tmp_path, 'wb+') as destination:
                for chunk in zip_file.chunks():
                    destination.write(chunk)
            process_canvas_zip.delay(tmp_path, course.id)
            return redirect('upload_success')
    else:
        form = CanvasJSONUploadForm(user=request.user)

    return render(request, 'ingest/upload_canvas.html', {'form': form})






def upload_success(request):
    return render(request, 'ingest/success.html')

from django.contrib import messages
from .forms import YouTubeUploadForm
from .models import YouTubeVideo

from .utils import parse_transcript
from .tasks import process_youtube_chunks  # We'll add this next

@login_required
def upload_youtube(request):
    if request.method == 'POST':
        form = YouTubeUploadForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            url = form.cleaned_data['url']
            title = form.cleaned_data['title']
            transcript = form.cleaned_data['transcript']

            # Create video entry
            video = YouTubeVideo.objects.create(course=course, url=url, title=title)

            # Parse transcript into chunks
            raw_chunks = parse_transcript(transcript, chunk_word_limit=200, overlap_ratio=0.1)
            chunk_data = [{'text': text, 'timestamp': timestamp} for timestamp, text in raw_chunks]

            # Queue async embedding
            process_youtube_chunks.delay(video.id, chunk_data)

            messages.success(request, "YouTube video uploaded and is being processed.")
            return redirect('upload_youtube')
    else:
        form = YouTubeUploadForm()

    return render(request, 'ingest/upload_youtube.html', {'form': form})
