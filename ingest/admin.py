from django.contrib import admin
from .models import TranscriptChunk, VideoTranscript, CanvasChunk, Course, CanvasFile, CanvasPage, CanvasAssignment

@admin.register(VideoTranscript)
class VideoTranscriptAdmin(admin.ModelAdmin):
    list_display = ('url', 'year', 'datetime')

@admin.register(TranscriptChunk)
class TranscriptChunkAdmin(admin.ModelAdmin):
    list_display = ('text', 'timestamp')
    search_fields = ('text',)


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

@admin.register(CanvasChunk)
class CanvasChunkAdmin(admin.ModelAdmin):
    list_display = ('parent_type', 'parent_id', 'short_text', 'created_at')
    list_filter = ('parent_type', 'created_at')
    search_fields = ('text', 'cleaned_text')

    def short_text(self, obj):
        return (obj.cleaned_text or obj.text)[:50] + '...' if obj.text else ''
    short_text.short_description = "Chunk Preview"


from .models import YouTubeVideo, YouTubeChunk

class YouTubeChunkInline(admin.TabularInline):
    model = YouTubeChunk
    extra = 0
    readonly_fields = ('text', 'timestamp', 'embedding')
    can_delete = False
    show_change_link = True

@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'course', 'uploaded_at')
    search_fields = ('title', 'url', 'course__title')
    list_filter = ('course', 'uploaded_at')
    inlines = [YouTubeChunkInline]

@admin.register(YouTubeChunk)
class YouTubeChunkAdmin(admin.ModelAdmin):
    list_display = ('video', 'timestamp', 'short_text')
    search_fields = ('text', 'timestamp', 'video__title')
    list_filter = ('video',)

    def short_text(self, obj):
        return obj.text[:80] + ('...' if len(obj.text) > 80 else '')
    short_text.short_description = 'Text Preview'