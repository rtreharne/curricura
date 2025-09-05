from .semantic_search import safe_date

def group_results(filtered_chunks, sort_order="relevance"):
    groups = {}
    for chunk in filtered_chunks:
        key = chunk["group_key"]
        if key not in groups:
            groups[key] = {
                "course": f"{chunk['course_code']} – {chunk['course_title']} (Year {chunk['year']})",
                "type": chunk["source_type"],
                "filename": chunk["filename"],
                "link": chunk["link"],
                "link_text": chunk["link_text"],
                "date": chunk["date"],
                "snippets": [],
                "relevance_scores": [],
            }
        groups[key]["snippets"].append({
            "text": chunk["content"],
            "timestamp": chunk["timestamp"],
            "link": chunk["link"],
            "link_text": chunk["link_text"],
        })
        groups[key]["relevance_scores"].append(chunk["relevance"])
    results = []
    for g in groups.values():
        g["relevance"] = max(g["relevance_scores"]) if g["relevance_scores"] else 0
        results.append(g)
    if sort_order == "newest":
        results.sort(key=lambda r: safe_date(r["date"]), reverse=True)
    elif sort_order == "oldest":
        results.sort(key=lambda r: safe_date(r["date"]))
    else:
        results.sort(key=lambda r: r["relevance"], reverse=True)
    return results