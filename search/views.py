import re
import datetime
from django.utils.safestring import mark_safe
from django.shortcuts import render
from .utils.semantic_search import get_top_chunks, resolve_canvas_parent

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

def semantic_search_view(request):
    raw_query = request.GET.get("query", "").strip()
    selected_year = request.GET.get("year", "").strip()
    selected_course = request.GET.get("course", "").strip()
    selected_source = request.GET.get("source", "").strip()
    sort_order = request.GET.get("sort", "relevance")  # default is relevance

    # Detect GitHub-style filename search
    filename_query = ""
    query = raw_query
    match = re.search(r'filename:\s*(.+)', raw_query, re.IGNORECASE)
    if match:
        filename_query = match.group(1).strip()
        query = ""  # Disable semantic search

    results = []
    available_years = set()
    available_courses = set()
    search_performed = bool(raw_query)  # Track any query, not just semantic

    from ingest.models import VideoTranscript, CanvasFile, CanvasPage, CanvasAssignment

    # Always populate filters
    if not raw_query:
        # Collect all years
        transcript_years = VideoTranscript.objects.values_list("year", flat=True).distinct()
        canvas_years = CanvasFile.objects.values_list("course__year", flat=True).distinct()
        available_years.update(filter(None, transcript_years))
        available_years.update(filter(None, canvas_years))

        # Collect all course titles
        transcript_courses = VideoTranscript.objects.values_list("course_title", flat=True).distinct()
        canvas_courses = CanvasFile.objects.values_list("course__title", flat=True).distinct()
        available_courses.update(filter(None, transcript_courses))
        available_courses.update(filter(None, canvas_courses))

    # Filename search
    if filename_query:
        files = CanvasFile.objects.filter(filename__icontains=filename_query)
        for f in files:
            year = str(f.course.year) if f.course else "N/A"
            course_title = f.course.title if f.course else "Unknown Course"
            course_code = f.course.code if f.course else ""
            # Populate filters
            if year:
                available_years.add(year)
            if course_title:
                available_courses.add(course_title)

            # Apply filters
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

        # Sorting
        if sort_order == "newest":
            results = sorted(results, key=lambda r: safe_date(r["date"]), reverse=True)
        elif sort_order == "oldest":
            results = sorted(results, key=lambda r: safe_date(r["date"]))

    # Semantic search
    elif query:
        top_chunks = get_top_chunks(query)
        filtered_chunks = []

        # Build results list
        for score, chunk, source_type in top_chunks:
            if source_type == "transcript":
                year = str(chunk.transcript.year)
                course_title = chunk.transcript.course_title
                course_code = chunk.transcript.course_code
                link = chunk.transcript_url
                link_text = "Link to Video"
                date = chunk.transcript.datetime.date()
                timestamp = chunk.timestamp
                filename = None
                content = chunk.text
                source_label = "Lecture Transcript"
            else:
                parent = resolve_canvas_parent(chunk)
                if parent:
                    course = parent.course
                    course_title = course.title if course else "Unknown Course"
                    course_code = course.code if course else ""
                    year = str(course.year) if course else "N/A"
                    filename = getattr(parent, "filename", None)
                    link = getattr(parent, "file_url", None)
                    link_text = "Open File" if link else None
                else:
                    course_title = "Unknown Course"
                    course_code = ""
                    year = "N/A"
                    filename = None
                    link = None
                    link_text = None
                date = None
                timestamp = None
                content = chunk.text
                source_label = "Canvas Content"

            if year:
                available_years.add(year)
            if course_title:
                available_courses.add(course_title)

            if selected_year and year != selected_year:
                continue
            if selected_course and course_title != selected_course:
                continue
            if selected_source and selected_source != source_label:
                continue

            relevance = (1 - score) * 100
            highlighted_content = highlight_text(content, query)

            filtered_chunks.append({
                "course_code": course_code,
                "course_title": course_title,
                "year": year,
                "source_type": source_label,
                "filename": filename,
                "relevance": relevance,
                "content": highlighted_content,
                "link": link,
                "link_text": link_text,
                "timestamp": timestamp,
                "date": date,
                "popularity": "NA",
            })

        # Remove duplicates for Canvas Content
        seen_filenames = set()
        unique_chunks = []
        for result in filtered_chunks:
            if result["source_type"] == "Canvas Content":
                fname = result.get("filename")
                if fname in seen_filenames:
                    continue
                seen_filenames.add(fname)
            unique_chunks.append(result)
        filtered_chunks = unique_chunks

        # Sorting
        if sort_order == "newest":
            results = sorted(filtered_chunks, key=lambda r: safe_date(r["date"]), reverse=True)
        elif sort_order == "oldest":
            results = sorted(filtered_chunks, key=lambda r: safe_date(r["date"]))
        else:
            results = sorted(filtered_chunks, key=lambda r: r["relevance"], reverse=True)

    return render(request, "search/semantic_search.html", {
        "query": raw_query,
        "results": results,
        "search_performed": search_performed,
        "available_years": sorted(available_years),
        "available_courses": sorted(available_courses),
        "selected_year": selected_year,
        "selected_course": selected_course,
        "selected_source": selected_source,
        "sort_order": sort_order,
    })
