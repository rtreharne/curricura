from django.shortcuts import render


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


def demo(request):
    return render(request, "core/demo.html")

def semantic_search_demo(request):
    results = [
        {
            "course_code": "VETS101",
            "course_title": "Introduction to Immunology",
            "year": 1,
            "source_type": "Lecture Transcript",
            "relevance": 92,
            "content": "Vaccines work by introducing <span class='bg-yellow-200 font-medium'>antigens</span> that trigger an immune response without causing disease.",
            "link_text": "Transcript: 00:13:42",
            "link": True,
            "popularity": 38,
        },
        {
            "course_code": "VETS204",
            "course_title": "Comparative Pathology",
            "year": 2,
            "source_type": "Video Transcript",
            "relevance": 89,
            "content": "The immune system recognizes the <span class='bg-yellow-200 font-medium'>pathogen signature</span> introduced by the vaccine and generates memory cells.",
            "link_text": "Watch from 00:09:25",
            "link": True,
            "popularity": 27,
        },
        {
            "course_code": "VETS320",
            "course_title": "Clinical Immunology",
            "year": 3,
            "source_type": "Uploaded File",
            "relevance": 84,
            "content": "The use of adjuvants in <span class='bg-yellow-200 font-medium'>vaccine formulations</span> enhances the immune response in livestock.",
            "link_text": "teaching_notes_vaccines.pdf · Page 3",
            "link": False,
            "popularity": 19,
        },
        {
            "course_code": "VETS440",
            "course_title": "Zoonotic Disease Control",
            "year": 4,
            "source_type": "Student Notes",
            "relevance": 81,
            "content": "Rabies vaccination programs rely on widespread <span class='bg-yellow-200 font-medium'>immunisation strategies</span> in both domestic and wild populations.",
            "link_text": "case_notes_week7.md · Section 2",
            "link": False,
            "popularity": 12,
        },
        {
            "course_code": "VETS201",
            "course_title": "Animal Health and Disease",
            "year": 2,
            "source_type": "Lecture Transcript",
            "relevance": 77,
            "content": "Passive immunity occurs when <span class='bg-yellow-200 font-medium'>pre-formed antibodies</span> are transferred to an animal, offering temporary protection.",
            "link_text": "Transcript: 00:24:17",
            "link": True,
            "popularity": 14,
        },
        {
            "course_code": "VETS330",
            "course_title": "Veterinary Public Health",
            "year": 3,
            "source_type": "Uploaded File",
            "relevance": 73,
            "content": "In herd vaccination strategies, the goal is to achieve <span class='bg-yellow-200 font-medium'>herd immunity</span> through sufficient population coverage.",
            "link_text": "vph_module3_notes.pdf · Page 9",
            "link": False,
            "popularity": 9,
        },
    ]
    return render(request, "core/semantic_search_demo.html", {"results": results})


def ai_chat_demo(request):
    messages = [
        {"sender": "ai", "text": "Hi! I'm your AI assistant for Veterinary Science. What are you working on today?"},
        {"sender": "user", "text": "Can you explain how vaccines work in animals?"},
        {"sender": "ai", "text": "Sure! Vaccines introduce antigens—harmless parts of pathogens—that trigger an immune response without causing disease. This 'trains' the immune system to recognize future threats."},
        {"sender": "ai", "text": "Here’s a helpful guide: <a href='#' class='underline text-blue-600'>VetImmunoBasics.pdf</a>"},
        {"sender": "user", "text": "Can you give an example in livestock?"},
        {"sender": "ai", "text": "Absolutely. In cattle, clostridial vaccines are common. They're given subcutaneously and often require boosters."},
        {"sender": "ai", "text": "Watch this short video: <a href='#' class='underline text-blue-600'>Vaccine Administration in Cattle (2:30)</a>"},
        {"sender": "user", "text": "Are there any assessments linked to vaccine topics in Year 2 modules?"},
        {"sender": "ai", "text": "Yes! I found 2 assessments in Year 2 that focus on vaccination and immune response:"},
        {"sender": "ai", "text": "<strong>1. Case Report:</strong> 'Designing a Vaccination Protocol for Small Ruminants' – due Week 9 in <em>VETS204</em>"},
        {"sender": "ai", "text": "<strong>2. MCQ Exam:</strong> 'Immunology Foundations' – includes 12 questions related to vaccine action and herd immunity."},
        {"sender": "ai", "text": "Let me know if you’d like sample questions or marking criteria."},
    ]
    return render(request, "core/ai_chat_demo.html", {"messages": messages})


