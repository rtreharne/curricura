from django.contrib import admin
from .models import TranscriptUpload



@admin.register(TranscriptUpload)
class TranscriptUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at', 'year')
    list_filter = ('year', 'uploaded_at')
    search_fields = ('file',)
    ordering = ('-uploaded_at',)
