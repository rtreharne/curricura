from django.db import models
    

class VideoTranscript(models.Model):
    YEAR_CHOICES = [(i, f'Year {i}') for i in range(1, 6)]

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
    embedding = models.JSONField(blank=True, null=True)
    transcript_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.transcript} @ {self.timestamp}"
