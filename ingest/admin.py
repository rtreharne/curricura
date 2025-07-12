from django.contrib import admin
from .models import TranscriptChunk, VideoTranscript

@admin.register(VideoTranscript)
class VideoTranscriptAdmin(admin.ModelAdmin):
    list_display = ('url', 'year', 'datetime')

@admin.register(TranscriptChunk)
class TranscriptChunkAdmin(admin.ModelAdmin):
    list_display = ('text', 'timestamp')
    search_fields = ('text',)
