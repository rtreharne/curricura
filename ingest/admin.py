from django.contrib import admin
from .models import TranscriptChunk, VideoTranscript

@admin.register(VideoTranscript)
class VideoTranscriptAdmin(admin.ModelAdmin):
    list_display = ('url', 'year', 'datetime')

@admin.register(TranscriptChunk)
class TranscriptChunkAdmin(admin.ModelAdmin):
    list_display = ('text', 'timestamp')
    search_fields = ('text',)

from django.contrib import admin
from .models import Course, CanvasFile, CanvasPage, CanvasAssignment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'year', 'created_at')
    search_fields = ('code', 'title')
    list_filter = ('year',)


@admin.register(CanvasFile)
class CanvasFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'course', 'canvas_file_id', 'created_at')
    search_fields = ('filename', 'text')
    list_filter = ('course',)


@admin.register(CanvasPage)
class CanvasPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'canvas_course_id', 'created_at')
    search_fields = ('title', 'text', 'url')
    list_filter = ('course',)


@admin.register(CanvasAssignment)
class CanvasAssignmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'assignment_id', 'points_possible', 'due_at', 'created_at_canvas')
    search_fields = ('name', 'description', 'html_url')
    list_filter = ('course', 'due_at', 'created_at_canvas')
