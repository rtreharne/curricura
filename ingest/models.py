from django.db import models
from pgvector.django import VectorField
    

class VideoTranscript(models.Model):
    YEAR_CHOICES = [(i, f'Year {i}') for i in range(1, 6)]
    course_code = models.CharField(max_length=20, blank=True)
    course_title = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(choices=YEAR_CHOICES)
    url = models.URLField()
    datetime = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcript for {self.url} ({self.get_year_display()})"


class TranscriptChunk(models.Model):
    transcript = models.ForeignKey(VideoTranscript, on_delete=models.CASCADE, related_name='chunks')
    text = models.TextField()
    cleaned_text = models.TextField(blank=True, null=True)
    timestamp = models.CharField(max_length=8)  # HH:MM:SS format
    embedding = VectorField(dimensions=1536, blank=True, null=True)
    transcript_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.transcript} @ {self.timestamp}"
