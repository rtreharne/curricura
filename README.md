# Curricura

**Curricura** is an AI-powered assistant that transforms exported Canvas course content and lecture transcripts into a searchable, conversational knowledge base. It allows students, instructors, and curriculum designers to ask natural language questions and receive accurate, context-aware answers based on course materials.

---

## 🧠 Overview

Curricura ingests:

- Exported Canvas course `.zip` files (pages, assignments, files, etc.)
- Accompanying transcript files (e.g., `.txt`, `.vtt`, `.srt`)

It processes, stores, and embeds this content using OpenAI’s embedding and language models, enabling a Retrieval-Augmented Generation (RAG) architecture for intelligent querying.

---

## 🎯 Why Curricura?

Learning Management Systems like Canvas often contain valuable course content—but accessing it can be inefficient and unintuitive.

Curricura solves this by turning static materials into a dynamic assistant that:

- Understands your course content
- Answers questions like *“Where are the oncology resources?”* or *“Give me an overview of assessments”*
- Supports both individual learning and institutional curriculum planning

---

## 👥 Who Benefits?

### 🧑‍🎓 Students
- Quickly locate lecture notes, assessments, or study resources
- Ask questions in natural language instead of hunting through menus
- Gain better orientation during revision or onboarding

### 🧑‍🏫 Instructors
- Verify clarity and structure of course delivery
- Easily surface or summarise key content
- Identify gaps or duplication in resources

### 🧑‍💼 Curriculum Designers
- Gain insight into course structure and coverage
- Explore topic distribution across modules
- Support curriculum mapping and quality assurance efforts

---

## ⚙️ How It Works

1. **Ingest**
   - Upload a Canvas `.zip` export and transcript files
   - Extract and parse content (pages, files, assignments, etc.)
   - Clean and store transcript text

2. **Embed**
   - Chunk course and transcript content
   - Generate OpenAI embeddings for each chunk
   - Store vectors in a searchable index (e.g., pgvector or FAISS)

3. **Chat**
   - Users ask questions via a chat interface
   - Queries are embedded and matched to the most relevant content chunks
   - GPT-4 generates responses grounded in your actual course materials

---

## 📦 Project Structure

curricura/
├── ingest/ # Parsing logic for Canvas zips and transcripts
├── embed/ # Chunking + embedding pipeline
├── chat/ # Chat interface and GPT logic
├── core/ # Django models and utilities
├── templates/ # Frontend templates
├── static/ # Static assets (JS, CSS)
├── manage.py
├── Dockerfile
└── docker-compose.yml

---

## 🚧 Development Roadmap (Current Phase: 1–3)

| Phase | Focus |
|-------|-------|
| 1     | Canvas and transcript ingestion |
| 2     | Embedding and vector indexing |
| 3     | Basic chat interface with GPT integration |
| 4     | Contextual enhancements and filtering |
| 5     | Curriculum planning tools and structure visualisation |
| 6     | Admin tools and polish for internal use/testing |

---

## 🧪 Local Development

> ⚠️ Deployment is not required at this stage. Curricura runs fully locally.

Requirements:
- Docker
- OpenAI API key
- Canvas export `.zip` file
- Transcripts folder (optional)

Development setup and run instructions will be added soon.

---

## 📜 License

MIT License

---

## ✨ Project Name Origin

**Curricura** blends *curriculum* and the Latin *cura* (“care” or “guidance”) — a name that reflects the project’s mission to make course content more accessible, understandable, and useful through AI.

