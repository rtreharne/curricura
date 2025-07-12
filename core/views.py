from django.shortcuts import render
from .utils import search_transcripts

def transcript_search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = search_transcripts(query)

    return render(request, 'core/search.html', {
        'query': query,
        'results': results,
    })


def home(request):
    features = [
        {"title": "Semantic Search", "description": "Find exactly what you need in seconds, even in messy module guides or lecture transcripts."},
        {"title": "Transcript Ingestion", "description": "Drop in .tsv files and ask questions — Curricura handles the rest."},
        {"title": "Canvas Zip Support", "description": "Upload full Canvas exports and query by assignment, page, or outcome."},
        {"title": "Gap Analysis", "description": "See where content is missing or duplicated. No more content blind spots."},
        {"title": "Balanced Assessment Checks", "description": "Identify overloaded modules or gaps in assessment types."},
        {"title": "LTI Integration", "description": "Plug Curricura into Canvas or any LTI platform. Students don’t even need to log in."},
        {"title": "De-identification", "description": "Names and identifiers are stripped from transcripts for privacy-preserving analytics."},
        {"title": "Admin Dashboard", "description": "See coverage, gaps, and trends across courses with zero manual auditing."},
        {"title": "Background Processing", "description": "Large files? No problem. We queue and process with Celery in the background."},
    ]
    return render(request, "core/home.html", {"features": features})

