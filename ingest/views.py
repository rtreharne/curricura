from django.shortcuts import render, redirect
from .forms import TranscriptUploadForm
from .models import TranscriptUpload

from ingest.tasks import process_transcript

from django.db import transaction
from ingest.tasks import process_transcript

import logging
logger = logging.getLogger(__name__)

def upload_transcript(request):
    if request.method == 'POST':
        form = TranscriptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()

            def enqueue():
                logger.info(f"Enqueuing transcript ID {instance.id}")
                process_transcript.delay(instance.id)

            transaction.on_commit(enqueue)

            return redirect('upload_success')
    else:
        form = TranscriptUploadForm()
    return render(request, 'ingest/upload.html', {'form': form})



def upload_success(request):
    return render(request, 'ingest/success.html')
