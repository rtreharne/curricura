from django.shortcuts import render
from .utils.semantic_search import get_top_chunks

def semantic_search_view(request):
    query = ""
    results = []

    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if query:
            results = get_top_chunks(query)

    return render(request, "search/semantic_search.html", {
        "query": query,
        "results": results
    })
