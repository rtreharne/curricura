from django.db import models
from pgvector.django import VectorField

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    year = models.IntegerField(choices=[(i, f'Year {i}') for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.title} ({self.year})"
    

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


class CanvasFile(models.Model):
    filename = models.CharField(max_length=255)
    course = models.ForeignKey('Course', null=True, blank=True, on_delete=models.CASCADE, related_name='canvas_files') 
    canvas_file_id = models.BigIntegerField()
    text = models.TextField()
    cleaned_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ('canvas_file_id', 'course')

    def __str__(self):
        return self.filename


class CanvasPage(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey('Course', null=True, blank=True, on_delete=models.CASCADE, related_name='canvas_pages') 
    url = models.SlugField(unique=True)
    canvas_course_id = models.BigIntegerField()
    text = models.TextField()
    cleaned_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CanvasAssignment(models.Model):
    assignment_id = models.BigIntegerField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='canvas_assignments', null=True, blank=True) 
    canvas_course_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    html_url = models.URLField()
    description = models.TextField(blank=True)
    cleaned_description = models.TextField(blank=True, null=True)
    points_possible = models.FloatField()
    due_at = models.DateTimeField(null=True, blank=True)
    created_at_canvas = models.DateTimeField(null=True, blank=True)
    updated_at_canvas = models.DateTimeField(null=True, blank=True)
    submission_types = models.JSONField()
    external_tool_url = models.URLField(blank=True, null=True)
    full_json = models.JSONField()  # Store full object for traceability
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment_id', 'canvas_course_id')

    def __str__(self):
        return self.name


class CanvasChunk(models.Model):
    PARENT_TYPE_CHOICES = [
        ('file', 'File'),
        ('page', 'Page'),
        ('assignment', 'Assignment')
    ]
    parent_type = models.CharField(max_length=20, choices=PARENT_TYPE_CHOICES)
    parent_id = models.PositiveIntegerField()
    text = models.TextField()
    cleaned_text = models.TextField(blank=True, null=True)
    embedding = VectorField(dimensions=1536, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['parent_type', 'parent_id']),
        ]

    def __str__(self):
        return f"{self.parent_type} {self.parent_id}"
