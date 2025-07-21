
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

def upload_transcript_tsv(request):
    if request.method == 'POST':
        form = TranscriptTSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            tsv_file = request.FILES['tsv_file']
            selected_year = int(form.cleaned_data['year'])
            course_code = form.cleaned_data['course_code']
            course_title = form.cleaned_data['course_title']

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
                    dt = datetime.strptime(f"{rows[0]['date']} {rows[0]['time']}", "%m/%d/%Y %I:%M %p")
                except Exception as e:
                    print(f"[ERROR] Failed to parse datetime for {url}: {e}")
                    continue

                vt = VideoTranscript.objects.create(
                    url=url,
                    datetime=dt,
                    year=selected_year,
                    course_code=course_code,
                    course_title=course_title,
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


from .forms import CanvasJSONUploadForm
from .models import CanvasFile, CanvasPage, CanvasAssignment

import zipfile
import tempfile
from .tasks import process_canvas_zip
import os
import tempfile
import shutil

from django.conf import settings

def upload_canvas_json(request):
    if request.method == 'POST':
        form = CanvasJSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.cleaned_data['course']
            zip_file = request.FILES['zip_file']

            # Save to persistent tmp directory
            tmp_filename = f"{course.id}_{zip_file.name}"
            tmp_path = os.path.join(settings.TMP_CANVAS_ZIP_DIR, tmp_filename)

            with open(tmp_path, 'wb+') as destination:
                for chunk in zip_file.chunks():
                    destination.write(chunk)

            # Queue task
            process_canvas_zip.delay(tmp_path, course.id)
            return redirect('upload_success')
    else:
        form = CanvasJSONUploadForm()

    return render(request, 'ingest/upload_canvas.html', {'form': form})





def upload_success(request):
    return render(request, 'ingest/success.html')