from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from pgvector.django import CosineDistance
from openai import OpenAI
from ingest.models import TranscriptChunk, CanvasChunk, YouTubeChunk
from .models import ChatSession, ChatMessage
import numpy as np
import json
import os
from ingest.models import CanvasFile, CanvasPage, CanvasAssignment, Course


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -----------------------------
# Utility Functions
# -----------------------------

def embed_query(text):
    """Generate an embedding vector for a user query."""
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding).tolist()


def get_or_create_session(request):
    """Retrieve or create a ChatSession linked to the user's session."""
    session_id = request.session.get("chat_session_id")
    if session_id:
        try:
            return ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            pass
    chat_session = ChatSession.objects.create()
    request.session["chat_session_id"] = chat_session.id
    return chat_session


def build_source_entry(chunk, source_type):
    """Build a dictionary entry for a chunk with extra metadata."""
    link = ""
    link_text = ""
    filename = ""
    course = ""

    if source_type == "Transcript":
        link = getattr(chunk, "transcript_url", "") or ""
        link_text = "View Transcript"
        if chunk.transcript and chunk.transcript.course:
            course = str(chunk.transcript.course)

    elif source_type == "Canvas":
        # Determine filename or title
        if chunk.parent_type == "file":
            try:
                canvas_file = CanvasFile.objects.get(id=chunk.parent_id)

                filename = canvas_file.filename
                link = canvas_file.file_url or ""
                course_obj = Course.objects.get(id=canvas_file.course_id)
                course = f"{course_obj.code} - {course_obj.title}"

                

            except AttributeError:
                filename = "Canvas File"

        elif chunk.parent_type == "page":
            try:
                filename = chunk.parent_page.title
            except AttributeError:
                filename = "Canvas Page"
        elif chunk.parent_type == "assignment":
            try:
                filename = chunk.parent_assignment.name
            except AttributeError:
                filename = "Canvas Assignment"

        #link = getattr(chunk, "file_url", "") or ""
        link_text = "Open Canvas File" if link else ""
        # Attempt to get course from parent relationship
        # try:
        #     course = str(chunk.parent_file.course or "")
        # except AttributeError:
        #     course = ""

    elif source_type == "YouTube":
        video = getattr(chunk, "video", None)
        link = getattr(video, "url", "") or ""
        link_text = "Watch on YouTube"
        if video and video.course:
            course = str(video.course)

    print("LINK:", link)
    return {
        "type": source_type,
        "id": chunk.id,
        "text": chunk.text or "",
        "distance": float(getattr(chunk, "distance", 0)),
        "link": link,
        "timestamp": getattr(chunk, "timestamp", "") or "",
        "link_text": link_text,
        "filename": filename,
        "course": course,
    }

def get_top_chunks(query_embedding, limit=5):
    """
    Retrieve top chunks from TranscriptChunk, CanvasChunk, and YouTubeChunk.
    Returns a combined, distance-ranked list.
    """
    transcript_chunks = (
        TranscriptChunk.objects
        .annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[:limit]
    )

    canvas_chunks = (
        CanvasChunk.objects
        .annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[:limit]
    )

    youtube_chunks = (
        YouTubeChunk.objects
        .annotate(distance=CosineDistance("embedding", query_embedding))
        .order_by("distance")[:limit]
    )

    combined = (
        [build_source_entry(c, "Transcript") for c in transcript_chunks] +
        [build_source_entry(c, "Canvas") for c in canvas_chunks] +
        [build_source_entry(c, "YouTube") for c in youtube_chunks]
    )

    return sorted(combined, key=lambda x: x["distance"])[:limit]


# -----------------------------
# Views
# -----------------------------

def chat_home(request):
    """Render the chat home page with session messages."""
    session_id = request.session.get("chat_session_id")
    messages = []
    if session_id:
        try:
            chat_session = ChatSession.objects.get(id=session_id)
            messages = chat_session.messages.order_by("created_at")
        except ChatSession.DoesNotExist:
            pass

    return render(request, "chat/chat.html", {
        "initial_instruction": "👋 Ask me anything about your lectures. I’ll reply using the most relevant parts of the course materials.",
        "messages": messages,
    })


@csrf_exempt
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()
        expansive = data.get("expansive", False)

        if not query:
            return JsonResponse({"error": "Query cannot be empty"}, status=400)

        chat_session = get_or_create_session(request)
        ChatMessage.objects.create(session=chat_session, is_user=True, message=query)

        query_embedding = embed_query(query)
        top_chunks = get_top_chunks(query_embedding, limit=5)

        context = "\n\n".join([f"[{c['type']}] {c['text']}" for c in top_chunks])

        system_message = (
            "You are a helpful assistant answering questions based on multiple sources: "
            "lecture transcripts, Canvas content, and YouTube videos. "
            "If the answer is not present, say 'I don't know'.\n\n"
            f"Context:\n{context}"
        )

        if expansive:
            system_message = (
                "You are a helpful assistant. Use the provided course materials where relevant, "
                "but feel free to incorporate external knowledge if necessary.\n\n"
                f"Course Context:\n{context}"
            )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]

        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.4 if expansive else 0.2,
        )

        answer = completion.choices[0].message.content
        ChatMessage.objects.create(session=chat_session, is_user=False, message=answer)

        return JsonResponse({"answer": answer, "sources": top_chunks})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

