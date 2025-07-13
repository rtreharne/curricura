from django.shortcuts import render
from .utils.semantic_search import get_top_chunks

def semantic_search_view(request):
    query = request.GET.get("query", "").strip()
    selected_year = request.GET.get("year", "").strip()
    selected_course = request.GET.get("course", "").strip()
    sort_order = request.GET.get("sort", "relevance")  # default is relevance

    results = []
    available_years = set()
    available_courses = set()

    if query:
        top_chunks = get_top_chunks(query)

        filtered_chunks = []
        for score, chunk in top_chunks:
            year = str(chunk.transcript.year)
            course_title = chunk.transcript.course_title

            available_years.add(year)
            available_courses.add(course_title)

            if selected_year and year != selected_year:
                continue
            if selected_course and course_title != selected_course:
                continue

            relevance = (1 - chunk.similarity) * 100
            filtered_chunks.append({
                "course_code": chunk.transcript.course_code,
                "course_title": course_title,
                "year": year,
                "source_type": "Lecture Transcript",
                "relevance": relevance,
                "content": chunk.text,
                "link": chunk.transcript_url,
                "link_text": "Link to Video",
                "timestamp": chunk.timestamp,
                "date": chunk.transcript.datetime.date(),
                "popularity": "NA"
            })

        if sort_order == "newest":
            results = sorted(filtered_chunks, key=lambda r: r["date"], reverse=True)
        elif sort_order == "oldest":
            results = sorted(filtered_chunks, key=lambda r: r["date"])
        else:  # sort by relevance (default)
            results = sorted(filtered_chunks, key=lambda r: r["relevance"], reverse=True)

    return render(request, "search/semantic_search.html", {
        "query": query,
        "results": results,
        "available_years": sorted(available_years),
        "available_courses": sorted(available_courses),
        "selected_year": selected_year,
        "selected_course": selected_course,
        "sort_order": sort_order,
    })
