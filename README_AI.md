# Echolabs – AI Integration (Part 2)

This document describes the AI workflow, data flow, and safety measures for the Echolabs Django application.

## Data Input

- **Conversations** are stored in the database: each `Conversation` has a user, title, `recorded_at`, and optional `duration_seconds`.
- **Transcript text** comes from `TranscriptSegment` records: each segment has `text` and `segment_order`. The full transcript sent to the LLM is built by concatenating segment text in order (see “Preprocessing” below).
- **Where it’s captured**: Users open a conversation’s detail page (`/conversations/<id>/`). They trigger “Generate summary” (local model) or “Get action items” (external API) via buttons. The backend reads the conversation’s segments from the database; no free-text input is required from the user for these two features.

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

## Safety Guardrails

- **Authorization**: Only the conversation owner can request a summary or action items for that conversation (user id is checked in `api_summarize_conversation` and `api_action_items`).
- **Input limits**: Transcript length is capped (2000 chars for local model, 2000 for external prompt, 4000 for API `text`). This reduces risk of excessive load and avoids oversized payloads.
- **Errors**: If the local model or external API fails, the views return JSON with an `error` (and optional `detail`) instead of raising. The UI shows the error message so users see a clear fallback instead of a broken response.
- **Secrets**: API keys (e.g. `HF_TOKEN` for Hugging Face Inference) are read from the environment (e.g. `.env`) and are not committed to the repo (`.env` is in `.gitignore`).
- **No arbitrary user prompts**: The two AI features use fixed prompts (summarization and action-item extraction). User-supplied free text is not passed directly as the sole prompt, which limits prompt-injection surface.

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
