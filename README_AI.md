# Echolabs – AI Integration (Part 2)

This document describes the AI workflow, data flow, and safety measures for the Echolabs Django application.

## Data Input

- **Conversations** are stored in the database: each `Conversation` has a user, title, `recorded_at`, and optional `duration_seconds`.
- **Transcript text** comes from `TranscriptSegment` records: each segment has `text` and `segment_order`. The full transcript sent to the LLM is built by concatenating segment text in order (see “Preprocessing” below).
- **Where it’s captured**: Users open a conversation’s detail page (`/conversations/<id>/`). They trigger “Generate summary” (local model) or “Get action items” (external API) via buttons. The backend reads the conversation’s segments from the database; no free-text input is required from the user for those two features.
- **Coach search (semantic retrieval)**: On **Insights** (`/insights/`), users type a **query** in a form and submit. The backend embeds the query with `sentence-transformers` and ranks passages from `conversations/data/coach_knowledge.md` (no database transcript for this feature).

## Preprocessing

- **Local summarization (Hugging Face BART)**  
  - Transcript is built from `Conversation.segments` ordered by `segment_order`, joined with spaces.  
  - The string is normalized: consecutive whitespace is collapsed and the result is stripped.  
  - Input is truncated to 2000 characters before sending to the model to stay within token limits and avoid overload.  
  - The prompt prefix `"Summarize what this person said in 1-2 sentences: "` is prepended; the tokenizer then truncates to 512 tokens if needed.

- **External API (Hugging Face Inference – action items)**  
  - The same segment-based transcript is used (or the raw `text` field from the request body if provided).  
  - The prompt is: `"List 3 action items from the following text in short bullet points:\n\n" + transcript`.  
  - Transcript is truncated to 2000 characters before being sent to the API.  
  - Request body is limited to 4000 characters for the `text` field when using the JSON API.

- **Coach search (sentence-transformers)**  
  - The knowledge file is split on blank lines into paragraphs; markdown heading lines (`# …`) are skipped; long paragraphs are split by word count so each chunk stays within a bounded size.  
  - The user query is stripped and capped at 500 characters before embedding.

## Safety Guardrails

- **Authorization**: Only the conversation owner can request a summary or action items for that conversation (user id is checked in `api_summarize_conversation` and `api_action_items`).
- **Input limits**: Transcript length is capped (2000 chars for local model, 2000 for external prompt, 4000 for API `text`). This reduces risk of excessive load and avoids oversized payloads.
- **Errors**: If the local model or external API fails, the views return JSON with an `error` (and optional `detail`) instead of raising. The UI shows the error message so users see a clear fallback instead of a broken response.
- **Secrets**: API keys (e.g. `HF_TOKEN` for Hugging Face Inference) are read from the environment (e.g. `.env`) and are not committed to the repo (`.env` is in `.gitignore`).
- **No arbitrary user prompts**: Summarization and action-item extraction use fixed prompts around transcript text; user text is not the sole system prompt, which limits prompt-injection surface. Coach search uses the user query only for **similarity matching** against a fixed corpus (retrieval), not as raw instructions to a generative model.

## Local LLM Integration

- **Model**: `philschmid/bart-large-cnn-samsum`, loaded via the `transformers` library (same model and approach as in `llm-test/ai_prototype.ipynb`).
- **Where**: `conversations/summarize.py` loads the tokenizer and model on first use and caches them. The view `api_summarize_conversation` (e.g. `GET /api/summarize/<id>/`) builds the transcript for the given conversation, calls `summarize_transcript()`, and returns `{"summary": "..."}` as JSON.
- **Usage**: On the conversation detail page, the “Generate summary” button calls this endpoint and displays the returned summary. The first request may be slower while the model is downloaded and loaded; subsequent requests reuse the in-memory model.

## API Integration (Second AI Feature)

- **Feature**: “Get action items” – given a conversation’s transcript, an external API returns a short list of action items (e.g. bullet points).
- **Provider**: Hugging Face Inference API (`https://api-inference.huggingface.co/models/google/flan-t5-base`). This is a separate AI feature from the local summarization and satisfies the requirement for a second AI feature via an external API.
- **Configuration**: Set `HF_TOKEN` (or `HUGGINGFACE_TOKEN`) in `.env` with a Hugging Face API token. If the token is missing, the action-items endpoint returns 503 with a message asking to configure it.
- **Usage**: On the conversation detail page, “Get action items” sends a POST request to `/api/action-items/` with JSON `{"conversation_id": <id>}`. The backend builds the transcript, calls the Hugging Face Inference API with the action-items prompt, and returns `{"action_items": "..."}`. The UI displays the result in the “Action items” section.

## Summary

| Component        | Data source              | Preprocessing                    | Safety / limits                          |
|-----------------|--------------------------|-----------------------------------|-----------------------------------------|
| Local summary   | `TranscriptSegment.text` | Join by order, normalize, truncate| Owner-only, length cap, error handling  |
| Action items    | Same transcript or body  | Truncate, fixed prompt            | Owner-only, length cap, HF token in .env |
| Coach search    | Form `query` on `/insights/` | Strip, max 500 chars; chunk corpus | Local embeddings only; no-match threshold; form errors |

## How prior assignments informed this build (A9)

### A6 — Model exploration (`llm-test/ai_prototype.ipynb`)

We benchmarked multiple Hugging Face seq2seq models on realistic conversation transcripts (BART and Flan-T5 families across size tiers). For **EchoLabs summarization**, `philschmid/bart-large-cnn-samsum` consistently produced short, faithful summaries of dialogue-style text compared with more generic CNN checkpoints, so it became the **production generative model** loaded in `conversations/summarize.py`.

### A7 — Performance, latency, and quality (`multimodel-system-test/`)

A7 added structured prompts, self-scored quality, and tokens/sec style observations across the same model families. The takeaway for Django: **smaller models** (e.g. Flan-T5-base) are attractive for latency when calling an **external** API (action items), while the **local** path tolerates a slightly heavier BART variant because it runs once per server process and is cached after the first load. Cost and routing notes in `multimodel-system-test/system_design.md` motivated keeping **summarization local** and **action items on Hugging Face Inference** as an optional second feature.

### A8 — Retrieval and embeddings (`rag-pipeline/`)

The RAG notebook compared **chunking strategies**, **three embedding sizes**, and **top-k retrieval** before generation. For the web app we port the **retrieval slice** of that pipeline: **sentence-transformers** over a small **on-disk coaching corpus** (`conversations/data/coach_knowledge.md`), **cosine similarity**, **top-k** results, and a **minimum similarity threshold** so the UI can show a clear “no good matches” state instead of irrelevant filler. Chunking follows **paragraph units** aligned with the “complete thought per chunk” rule from A8. The **medium** embedding model `sentence-transformers/multi-qa-mpnet-base-cos-v1` matches the A8 “medium” tier used in experiments (see `rag_system.ipynb` / `rag_analysis.md`).

### Semantic coach search (local — A8 in Django)

**Implemented:** **POST form on `/insights/`** → `insights_view` → `CoachSearchForm` → `conversations/coach_search.py`.

**Corpus:** `conversations/data/coach_knowledge.md` (paragraph-separated coaching passages for EchoLabs).

**Pipeline:** **sentence-transformers** (`multi-qa-mpnet-base-cos-v1`, same medium tier as `rag-pipeline/rag_system.ipynb`) embeds the query and all chunks; **cosine similarity** ranks passages; **top-k** with a **minimum score** (`MIN_SCORE` in code) returns either ranked passages with scores in the template or a clear **no retrieved results** message. Uses **only** local open weights (no paid API).

### Guardrails (summary)

| Case | Behavior |
|------|-----------|
| Empty transcript (summary / action items) | JSON error or empty-state message in UI |
| Empty or whitespace-only coach query | Form validation error on `/insights/` |
| No chunks above similarity cutoff | User-visible message on `/insights/`; no invented passages |
| HF Inference errors | HTTP status preserved; JSON includes `detail` from HF `error` when present |
| Oversized inputs | Character limits on transcript, API body, and coach query |
