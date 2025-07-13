from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import F
from pgvector.django import CosineDistance
from openai import OpenAI
from ingest.models import TranscriptChunk
import numpy as np
import json
import os

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat_home(request):
    return render(request, "chat/chat.html", {
        "initial_instruction": "👋 Ask me anything about your lectures. I’ll reply using the most relevant parts of the transcript."
    })



def embed_query(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding).tolist()

@csrf_exempt
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()
        if not query:
            return JsonResponse({"error": "Query cannot be empty"}, status=400)

        # Embed the user query
        query_embedding = embed_query(query)

        # Search top 5 relevant chunks using cosine distance in Postgres
        top_chunks = (
            TranscriptChunk.objects
            .annotate(distance=CosineDistance("embedding", query_embedding))
            .order_by("distance")[:5]
        )

        # Construct the context string
        context = "\n\n".join([chunk.text for chunk in top_chunks])

        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant answering questions based on lecture transcripts. Here are some relevant excerpts:\n\n{context}"
            },
            {
                "role": "user",
                "content": query
            }
        ]

        # Get chat completion from OpenAI
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2
        )

        answer = completion.choices[0].message.content
        return JsonResponse({"answer": answer})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
