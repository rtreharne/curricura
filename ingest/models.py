from django.db import models

class TranscriptUpload(models.Model):
    YEAR_CHOICES = [(i, f'Year {i}') for i in range(1, 6)]

    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='transcripts/')
    description = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(choices=YEAR_CHOICES)

    cleaned_text = models.TextField(blank=True, null=True)
    embedding = models.JSONField(blank=True, null=True)  # Stores list of floats

    def __str__(self):
        return f'{self.file.name} ({self.get_year_display()})'
