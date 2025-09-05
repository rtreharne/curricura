import re
import datetime
from django.utils.safestring import mark_safe
from django.shortcuts import render
from .utils.semantic_search import get_top_chunks, resolve_canvas_parent
from django.contrib.auth.decorators import login_required
from ingest.models import Course, VideoTranscript, TranscriptChunk, CanvasFile


def safe_date(value):
    """
    Ensures a comparable date for sorting, using datetime.date.min if None or invalid.
    """
    return value if isinstance(value, (datetime.date, datetime.datetime)) else datetime.date.min

def highlight_text(text, query):
    """
    Highlights all occurrences of the query in the text.
    """
    if not query or not text:
        return text
    escaped_query = re.escape(query)
    pattern = re.compile(rf"({escaped_query})", re.IGNORECASE)
    highlighted = pattern.sub(r'<mark>\1</mark>', text)
    return mark_safe(highlighted)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ingest.models import VideoTranscript, CanvasFile
from core.models import School
import re

import re
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ingest.models import VideoTranscript, CanvasFile, YouTubeVideo, Course
from search.utils.semantic_search import get_top_chunks, resolve_canvas_parent

@login_required
def semantic_search_view(request):
    raw_query = request.GET.get("query", "").strip()
    selected_year = request.GET.get("year", "").strip()
    selected_course = request.GET.get("course", "").strip()
    selected_source = request.GET.get("source", "").strip()
    selected_school = request.GET.get("school", "").strip()
    sort_order = request.GET.get("sort", "relevance")  # default is relevance

    # Detect filename search
    filename_query = ""
    query = raw_query
    match = re.search(r'filename:\s*(.+)', raw_query, re.IGNORECASE)
    if match:
        filename_query = match.group(1).strip()
        query = ""  # Disable semantic search

    results = []
    available_years = set()
    available_courses = set()
    available_schools = set()
    search_performed = bool(raw_query)

    # Determine allowed schools for current user
    user_school_ids = []
    if hasattr(request.user, "profile"):
        user_schools = request.user.profile.schools.all()
        user_school_ids = list(user_schools.values_list("id", flat=True))
        available_schools.update(s.name for s in user_schools)

    def filter_by_school(queryset):
        if selected_school:
            return queryset.filter(course__schools__name=selected_school)
        if user_school_ids:
            return queryset.filter(course__schools__id__in=user_school_ids)
        return queryset

    # Populate filter dropdowns
    #if not raw_query:
    transcript_years = filter_by_school(VideoTranscript.objects).values_list("course__year", flat=True).distinct()
    canvas_years = filter_by_school(CanvasFile.objects).values_list("course__year", flat=True).distinct()
    youtube_years = filter_by_school(YouTubeVideo.objects).values_list("course__year", flat=True).distinct()
    available_years.update(filter(None, transcript_years))
    available_years.update(filter(None, canvas_years))
    available_years.update(filter(None, youtube_years))

    available_courses = Course.objects.filter(
        schools__in=user_school_ids
    ).distinct()

    # ----------------------------
    # Filename search (Canvas files)
    # ----------------------------
    if filename_query:
        files = filter_by_school(CanvasFile.objects.filter(filename__icontains=filename_query))
        for f in files:
            course = f.course
            year = str(course.year) if course else "N/A"
            course_title = course.title if course else "Unknown Course"
            course_code = course.code if course else ""

            if selected_year and year != selected_year:
                continue
            if selected_course and course_title != selected_course:
                continue
            if selected_source and selected_source != "Canvas Content":
                continue

            results.append({
                "course_code": course_code,
                "course_title": course_title,
                "year": year,
                "source_type": "Canvas Content",
                "filename": f.filename,
                "relevance": None,
                "content": highlight_text((f.cleaned_text or f.text)[:300], filename_query),
                "link": f.file_url,
                "link_text": "Open File" if f.file_url else None,
                "timestamp": None,
                "date": f.created_at,
                "popularity": "NA",
            })

        if sort_order == "newest":
            results.sort(key=lambda r: safe_date(r["date"]), reverse=True)
        elif sort_order == "oldest":
            results.sort(key=lambda r: safe_date(r["date"]))

    # ----------------------------
    # Semantic search (transcripts + Canvas + YouTube)
    # ----------------------------
    elif query:
        top_chunks = get_top_chunks(query)  # Now returns transcript, canvas, or youtube chunks
        filtered_chunks = []

        for score, chunk, source_type in top_chunks:
            course = None
            source_label = None
            filename = None
            link = None
            link_text = None
            date = None
            timestamp = None
            content = chunk.text

            # ---- Transcript Chunks ----
            if source_type == "transcript":
                course = chunk.transcript.course
                if not course:
                    continue
                source_label = "Lecture Transcript"
                link = chunk.transcript_url
                link_text = "Link to Video"
                date = chunk.transcript.datetime.date()
                timestamp = chunk.timestamp

            # ---- YouTube Chunks ----
            elif source_type == "youtube":
                video = chunk.video
                course = video.course
                if not course:
                    continue
                source_label = "YouTube Transcript"
                link = video.url
                link_text = "Watch Video"
                date = video.uploaded_at.date()
                timestamp = chunk.timestamp

            # ---- Canvas Chunks ----
            else:
                parent = resolve_canvas_parent(chunk)
                if not parent or not parent.course:
                    continue
                course = parent.course
                source_label = "Canvas Content"
                filename = getattr(parent, "filename", None)
                link = getattr(parent, "file_url", None)
                link_text = "Open File" if link else None

            # School filtering
            if selected_school and not course.schools.filter(name=selected_school).exists():
                continue
            if user_school_ids and not course.schools.filter(id__in=user_school_ids).exists():
                continue

            course_title = course.title
            course_code = course.code
            year = str(course.year)

            # Apply dropdown filters
            if selected_year and year != selected_year:
                continue
            if selected_course and course_title != selected_course:
                continue
            if selected_source and selected_source != source_label:
                continue

            relevance = (1 - score) * 100

            group_key = None
            if source_type == "transcript":
                group_key = f"transcript-{chunk.transcript.id}"
            elif source_type == "youtube":
                group_key = f"youtube-{chunk.video.id}"
            else:  # Canvas
                parent_id = getattr(parent, "id", None)
                parent_type = getattr(parent, "_meta", None)
                type_label = parent_type.model_name if parent_type else "canvas"
                group_key = f"canvas-{type_label}-{parent_id}"

            filtered_chunks.append({
                "course_code": course_code,
                "course_title": course_title,
                "year": year,
                "source_type": source_label,
                "filename": filename,
                "relevance": relevance,
                "content": highlight_text(content, query),
                "link": link,
                "link_text": link_text,
                "timestamp": timestamp,
                "date": date,
                "popularity": "NA",
                "group_key": group_key,
            })

        # Group results by group_key
        groups = {}
        for chunk in filtered_chunks:
            key = chunk["group_key"]
            if key not in groups:
                groups[key] = {
                    "course_code": chunk["course_code"],
                    "course_title": chunk["course_title"],
                    "year": chunk["year"],
                    "source_type": chunk["source_type"],
                    "filename": chunk["filename"],
                    "link": chunk["link"],
                    "link_text": chunk["link_text"],
                    "date": chunk["date"],
                    "snippets": [],
                    "relevance_scores": [],
                    "timestamp": chunk["timestamp"],  # keep first one for now
                }
            groups[key]["snippets"].append({
                "content": chunk["content"],
                "timestamp": chunk["timestamp"],
                "link": chunk["link"],
                "link_text": chunk["link_text"],
            })
            groups[key]["relevance_scores"].append(chunk["relevance"])

        # Flatten back into a results list (groups only)
        results = []
        for group in groups.values():
            group["relevance"] = max(group["relevance_scores"]) if group["relevance_scores"] else 0
            results.append(group)

        # Apply sorting
        if sort_order == "newest":
            results.sort(key=lambda r: safe_date(r["date"]), reverse=True)
        elif sort_order == "oldest":
            results.sort(key=lambda r: safe_date(r["date"]))
        else:  # relevance
            results.sort(key=lambda r: r["relevance"], reverse=True)
            
        print(f"Total grouped results: {len(results)}")
        print(results)

    return render(request, "search/semantic_search.html", {
        "query": raw_query,
        "results": results,
        "search_performed": search_performed,
        "available_years": sorted(available_years),
        "available_courses": available_courses,
        "available_schools": sorted(available_schools),
        "selected_year": selected_year,
        "selected_course": selected_course,
        "selected_source": selected_source,
        "selected_school": selected_school,
        "sort_order": sort_order,
    })