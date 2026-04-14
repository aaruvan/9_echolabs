# Echolabs – AI Integration (Part 2)

This document describes the AI workflow, data flow, and safety measures for the Echolabs Django application.

## Data Input

- **Conversations** are stored in the database: each `Conversation` has a user, title, `recorded_at`, and `duration_seconds` when duration is known.
- **Transcript text** comes from `TranscriptSegment` records: each segment has `text` and `segment_order`. The full transcript sent to the LLM is built by concatenating segment text in order (see “Preprocessing” below).
- **Where it’s captured**: Users open a conversation’s detail page (`/conversations/<id>/`). They trigger “Generate summary” (local model) or “Get action items” (external API) via buttons. The backend reads the conversation’s segments from the database; no free-text input is required from the user for those two features.
- **Coach search (semantic retrieval)**: On **Insights** (`/insights/`), users type a **query** in a form and submit. The backend embeds the query with `sentence-transformers` and ranks passages from `conversations/data/coach_knowledge.md` (no database transcript for this feature).

## Preprocessing

- **Local summarization (Hugging Face BART)**  
  - Transcript is built from `Conversation.segments` ordered by `segment_order`, joined with spaces.  
  - The string is normalized: consecutive whitespace is collapsed and the result is stripped.  
  - Input is truncated to 2000 characters before sending to the model to stay within token limits and avoid overload.  
  - The model receives **the transcript text only** (no instruction prefix), with a **minimum word-count floor** so very short placeholders do not trigger unreliable generations; the tokenizer truncates to 512 tokens if needed (see `conversations/summarize.py`).

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
- **Errors**: If the local model or external API fails, the views return JSON with an `error` and may include a `detail` field instead of raising. The UI shows the error message so users see a clear fallback instead of a broken response.
- **Secrets**: API keys (e.g. `HF_TOKEN` for Hugging Face Inference) are read from the environment (e.g. `.env`) and are not committed to the repo (`.env` is in `.gitignore`).
- **No arbitrary user prompts**: Summarization and action-item extraction use fixed prompts around transcript text; user text is not the sole system prompt, which limits prompt-injection surface. Coach search uses the user query only for **similarity matching** against a fixed corpus (retrieval), not as raw instructions to a generative model.

## Local LLM Integration

- **Model**: `philschmid/bart-large-cnn-samsum`, loaded via the `transformers` library (same model and approach as in `llm-test/ai_prototype.ipynb`).
- **Where**: `conversations/summarize.py` loads the tokenizer and model on first use and caches them. The view `api_summarize_conversation` (e.g. `GET /api/summarize/<id>/`) builds the transcript for the given conversation, calls `summarize_transcript()`, and returns `{"summary": "..."}` as JSON.
- **Usage**: On the conversation detail page, the “Generate summary” button calls this endpoint and displays the returned summary. The first request may be slower while the model is downloaded and loaded; subsequent requests reuse the in-memory model.

## API Integration (Second AI Feature)

- **Feature**: “Get action items” – given a conversation’s transcript, an external API returns a short list of action items (e.g. bullet points).
- **Provider**: Hugging Face Inference Providers via `huggingface_hub.InferenceClient.chat_completion`. Default model: `Qwen/Qwen2.5-7B-Instruct` (overridable via `HF_ACTION_ITEMS_MODEL` in `.env`). Separate from local summarization: hosted chat completion over the transcript.
- **Configuration**: Set `HF_TOKEN` (or `HUGGINGFACE_TOKEN`) in `.env` with a Hugging Face API token. If the token is missing, the action-items endpoint returns 503 with a message asking to configure it.
- **Usage**: On the conversation detail page, “Get action items” sends a POST request to `/api/action-items/` with JSON `{"conversation_id": <id>}`. The backend builds the transcript, calls the Hugging Face Inference Providers API with the action-items prompt, and returns `{"action_items": "..."}`. The UI displays the result in the “Action items” section.

## Summary

| Component        | Data source              | Preprocessing                    | Safety / limits                          |
|-----------------|--------------------------|-----------------------------------|-----------------------------------------|
| Local summary   | `TranscriptSegment.text` | Join by order, normalize, truncate| Owner-only, length cap, error handling  |
| Action items    | Same transcript or body  | Truncate, fixed prompt            | Owner-only, length cap, HF token in .env |
| Coach search    | Form `query` on `/insights/` | Strip, max 500 chars; chunk corpus | Local embeddings only; no-match threshold; form errors |

## How prior coursework informed this build

### A6 — Model exploration (`llm-test/ai_prototype.ipynb`)

We benchmarked multiple Hugging Face seq2seq models on realistic conversation transcripts (BART and Flan-T5 families across size tiers). For **EchoLabs summarization**, `philschmid/bart-large-cnn-samsum` consistently produced short, faithful summaries of dialogue-style text compared with more generic CNN checkpoints, so it became the **production generative model** loaded in `conversations/summarize.py`.

### A7 — Performance, latency, and quality (`multimodel-system-test/`)

A7 added structured prompts, self-scored quality, and tokens/sec style observations across the same model families. The takeaway for Django: **smaller models** (e.g. Flan-T5-base) are attractive for latency when calling an **external** API (action items), while the **local** path tolerates a slightly heavier BART variant because it runs once per server process and is cached after the first load. Cost and routing notes in `multimodel-system-test/system_design.md` motivated keeping **summarization local** and **action items on Hugging Face Inference** as the second feature.

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


## Part 2: Workflow and architecture

### Step 2.1: AI workflow

The subsections below focus on **summarization** and **semantic coach search**. **Action items** follow the Hugging Face Inference path in “API Integration (Second AI Feature)” above.

### Feature 1: Summarization

1. **User Input:** The user navigates to a conversation detail page and clicks "Generate Summary." This triggers a GET request to the summarization API with the conversation's primary key.

2. **Preprocessing:** The backend calls `_transcript_for_conversation(conversation)`, which queries all `TranscriptSegment` objects linked to the conversation, orders them by `segment_order`, and joins their `.text` fields into a single string with spaces.

3. **Model Used:** `philschmid/bart-large-cnn-samsum` via Hugging Face `transformers` (loaded locally via `summarize.py`). The model runs entirely on the local machine — no external API call is made.

4. **Output Generation:** The transcript text is passed to `summarize_transcript(transcript)`. The model produces an abstractive summary of the conversation.

5. **Response:** The view returns a `JsonResponse({"summary": summary})` which the frontend JavaScript on the detail page renders inline on the page.


### Feature 2: Semantic Coach Search 

1. **User Input:** The user types a natural-language query into the coach search form on the `/insights/` page (e.g., "how do I reduce filler words?"). The form is submitted via POST.

2. **Preprocessing:** The query is validated — empty queries and queries over 500 characters are rejected with a clear error message. The query string is passed to `coach_search.search(query)`.

3. **Knowledge Base + Embedding:** `coach_search.py` reads `conversations/data/coach_knowledge.md`, splits it into paragraphs (with a max of 220 words per chunk), and embeds all chunks using `sentence-transformers/multi-qa-mpnet-base-cos-v1`. Embeddings are cached in memory after the first load so subsequent queries are fast. The user's query is also embedded using the same model.

4. **Retrieval:** Cosine similarity is computed between the query embedding and all chunk embeddings using `sklearn.metrics.pairwise.cosine_similarity`. The top 5 results are considered, and any chunk scoring below 0.28 (the `MIN_SCORE` threshold) is filtered out.

5. **Response:** Matching chunks and their similarity scores are returned to `insights_view`, which passes them to the `conversations/insights.html` template for display. If no chunks clear the threshold, a `coach_no_match` message is shown instead.

---

### Step 2.2: Architecture Explanation

### Feature 1: Summarization

```
User (clicks "Generate Summary" on detail page)
        |
        v
Django View: api_summarize_conversation
        |
        |--> _transcript_for_conversation(conversation)
        |         Queries TranscriptSegment objects
        |         Joins text in order → full transcript string
        |
        |--> summarize_transcript(transcript)   [summarize.py]
        |         Loads philschmid/bart-large-cnn-samsum via transformers
        |         Runs local inference on CPU/GPU
        |
        v
JsonResponse({"summary": "..."})
        |
        v
JavaScript on conversation_detail.html renders summary inline
```

### Feature 2: Semantic Coach Search (RAG-style)

```
User (types query into CoachSearchForm on /insights/)
        |
        v
Django View: insights_view(request)  [POST]
        |
        |--> CoachSearchForm validation
        |         Rejects empty or >500 character queries
        |
        |--> coach_search.search(query)
        |         |
        |         |--> _ensure_index()
        |         |       Reads coach_knowledge.md
        |         |       Splits into paragraphs (≤220 words)
        |         |       Embeds all chunks with multi-qa-mpnet-base-cos-v1
        |         |       Caches embeddings in memory
        |         |
        |         |--> Embeds user query (same model)
        |         |
        |         |--> cosine_similarity(query_emb, chunk_embeddings)
        |         |
        |         |--> Filters top-5 results by MIN_SCORE = 0.28
        |         |
        |         v
        |     Returns (results: List[{text, score}], no_match_msg)
        |
        v
insights.html renders matched passages or no-match message
```

---

### Step 2.3: Model Selection Rationale

### Summarization Model: `philschmid/bart-large-cnn-samsum`

**Selected model:** `philschmid/bart-large-cnn-samsum` (SamSum-fine-tuned BART; same choice as `conversations/summarize.py` and `llm-test/ai_prototype.ipynb`).

**Why this model:** This checkpoint was fine-tuned on the SAMSum dataset, which consists of real dialogue and conversation transcripts — the kind of content Echolabs processes. It produces abstractive summaries rather than only extracting sentences, which yields readable output for coaching-style conversations.

**Alternatives considered (from A6/A7):**
- `t5-small` and `flan-t5-base` were tested in earlier assignments. Both are faster and lighter, but produce lower-quality summaries for dialogue-style input. The outputs tended to be fragmented or miss the main point especially for larger transcripts
- `facebook/bart-large-cnn` (without samsum fine-tuning) was tested in A6 and scored 7/10 on summarization but echoed the prompt verbatim on every other task type (action extraction, sentiment, topic labeling), confirming it is only useful for news-style summarization, not conversational input.
- The Hugging Face Inference API drives the **action items** feature (`POST /api/action-items/`), separate from summarization — the primary summarization path runs locally with no generative API dependency.
- `sshleifer/distilbart-cnn-12-6` was the fastest model tested in A6 (~3.28s avg, 28–30 tok/s) and scored 9/10 on summarization in A7, but scored 0 on sentiment, topic labeling, and structured output — making it unreliable for anything beyond basic summarization. It was rejected in favor of a more broadly capable model.
- `facebook/bart-large-xsum` hallucinated entirely unrelated content on all five prompt types in A7 and was immediately eliminated.


**Why it fits the app:** Echolabs is built around conversation analysis and coaching feedback. A model fine-tuned on dialogue summarization aligns with that use case. Based on latency tests in A7, this BART SamSum checkpoint showed acceptable inference time (~2–4s on CPU for typical transcript lengths) with higher summary quality than smaller models we tried.


### Retrieval / Embedding Model: `sentence-transformers/multi-qa-mpnet-base-cos-v1`
 
**Selected model:** `sentence-transformers/multi-qa-mpnet-base-cos-v1`
 
**Why this model:** This model was specifically trained for semantic search and question-answering retrieval tasks — it is designed to match queries to relevant passages, not just find lexically similar text. The `cos-v1` suffix indicates it produces normalized embeddings optimized for cosine similarity, which is exactly the similarity metric used in the retrieval pipeline.
 
**Alternatives considered (from A8):**
- `multi-qa-MiniLM-L6-cos-v1` (small, 384d) was tested as the lightweight baseline in A8. It was faster but achieved a lower average context quality score (2.33) and answer quality (1.47) across the 45-run experiment.
- `BAAI/bge-large-en-v1.5` (large, 1024d) was the best performing model in A8 (context quality 2.87, answer quality 1.73) but was rejected for the Django integration because it is significantly heavier to load and hold in memory, making it unsuitable for a synchronous web request on a local machine.
- The medium model `multi-qa-mpnet-base-cos-v1` was selected as the practical balance — lighter than BGE-large while still purpose-built for query-passage retrieval tasks.
 
**Why it fits the app:** The coach search feature is a question-answering retrieval task — users ask coaching questions and the system finds relevant advice passages. The `multi-qa` family is purpose-built for exactly this pattern, and the medium tier offers acceptable quality without the memory overhead of the large model.


---

## Part 3: Evaluation

**Demo data:** `python manage.py seed_part3_eval` creates user **`part3_eval`** / password **`part3demo123`** and five conversations titled with the **`[Part3]`** prefix for the scenarios below.

---

### Step 3.1: Test cases

Coverage: **Transcribe** upload, seeded **`[Part3]`** conversations, **`/insights/`** coach search, and action items when **`HF_TOKEN`** is set.

| # | Scenario | User action | Outcome |
|---|----------|-------------|---------|
| **TC1** | **Transcribe audio, then summarize** | **`/conversations/transcribe/`** → upload (within app limits) → submit → open the created conversation → **Generate summary** | **Speech → WhisperX segments → local BART summary** on uploaded audio (outside the seed set). |
| **TC2** | **Summarize a seeded multi-speaker meeting** | **`[Part3] Summary — team sync`** → **Generate summary** | Local BART on a transcript with **`Speaker A:` / `Speaker B:`** lines (seed / diarized style). |
| **TC3** | **Summarize a too-short transcript** | **`[Part3] Summary — too short`** → **Generate summary** | Guardrail: error or explanation instead of hallucinating on minimal text. |
| **TC4** | **Coach knowledge search** | **`/insights/`** → query **`How can I slow down my speaking when I'm nervous?`** (see §3.2) | Sentence-transformers retrieval: ranked passages or no-match message. |
| **TC5** | **Action items from a check-in** | **`[Part3] Action items — project check-in`** → **Get action items** | Hugging Face Inference (`Qwen/Qwen2.5-7B-Instruct` by default): bullet-style follow-ups when `HF_TOKEN` is set. |

§3.4 compares plain transcript vs diarized output **on the same audio as TC1**.

---

### Step 3.2: Outputs

| Test case | Test input | Intended behavior | Observed output | Quality notes | Latency |
|-----------|------------|-------------------|-----------------|---------------|---------|
| **TC1** | **`/conversations/transcribe/`** → upload audio → open new conversation → **Generate summary** | Summary reflects meeting content; without speaker labels, output can read generically (**Failure 1**). | **Before:** plain transcript *without* speaker labels — blockquote **below**. **After:** diarized transcript in §3.4. | Much better after improvement | 230s |
| **TC2** | **`[Part3] Summary — team sync`**, **Generate summary** | One or two sentences summarizing the standup (blockers, timeline). | Speaker A shipped the login flow and the error states are in review. Speaker A is waiting on rate limit numbers from infra before he flips the beta flag. Speaker B and Speaker A will target Friday for beta if infra can confirm it can confirm by Wednesday. | used mock data with speakers set so pretty good | 20s |
| **TC3** | **`[Part3] Summary — too short`** | Message that transcript is too short / not summarized. | This transcript is too short to summarize reliably. Add more transcript segments or real spoken content, then try again. | - | <1s |
| **TC4** | Insights form query: **`How can I slow down my speaking when I'm nervous?`** | Top passages from `coach_knowledge.md` with scores, or no-match text. | **`coach_search` (local run):** **0.599** *Pacing matters as much as word choice…* (deliberate breath between sentences); **0.589** *Confidence is partly physiological…* box breathing vs rushed speech; **0.570** *Eye contact and posture…* grounded posture slows rushed patterns; **0.424** *Reducing defensiveness…* paraphrase before rebuttal; **0.402** *Handling silence…* count two seconds before filling gaps. | Strong on corpus-style queries; less representative of messy real transcripts until re-run on live UI. | ~4 min with cold start |
| **TC5** | **`[Part3] Action items — project check-in`**, **Get action items** | Short bullet list of follow-ups (timeline, retro, doc). | **Representative HF-style bullets:** `- Send the client the revised timeline by Thursday` · `- Schedule a 30-minute retro with design for the navigation issues` · `- Post the incident notes in the shared doc so everyone has the same source of truth` | Matches seeded ask (timeline, retro, doc). | ~2 min with cold start |

**TC1 — Before (plain transcript text, no speaker labels; same meeting as §3.4 “After”):**

> Hello everyone, thank you guys for coming to our weekly student success meeting and let's just get started. So I have our list of chronically absent students here and I've been noticing a troubling trend. A lot of students are skipping on Fridays. Does anyone have any idea what's going on? I've heard some of my mentees talking about how it's really hard to get out of bed on Fridays. It might be good if we did something like a pancake breakfast to encourage them to come. I think that's a great idea. Let's try that next week. It might also be because a lot of students have been getting sick now that it's getting colder outside. I've had a number of students come by my office with symptoms like sniffling and coughing. We should put up posters with tips for not getting sick since it's almost flu season, like, you know, wash your hands after the bathroom, stuff like that. I think that's a good idea and it'll be a good reminder for the teachers as well. So one other thing I wanted to talk about, there's a student I've noticed here, John Smith. He's missed seven days already and it's only November. Does anyone have an idea what's going on with him? I might be able to fill in the gaps there. I talked to John today and he's really stressed out. He's been dealing with helping his parents take care of his younger siblings during the day. It might actually be a good idea if he spoke to the guidance counselor a little bit. I can talk to John today if you want to send him to my office after you meet with him. It's a lot to deal with for middle schooler. Great thanks and I can help out with the family's childcare needs. I'll look for some free or low-cost resources in the community to share with John and he can share them with his family. Great, awesome really good ideas here today. Thanks for coming and if no one has anything else I think we can wrap up.

---

### Step 3.3: Failure analysis

#### Failure 1: Generic summary when the transcript does not show who said what

- **What happened:** After **TC1** (upload audio on **`/conversations/transcribe/`** → **Generate summary**), the BART summary reads **vague or generic**—e.g. it blends commitments and reactions without clearly attributing them to a specific person, or it sounds like a single narrator even when two people spoke.  
- **Why:** The summarizer (`summarize.py`) sees one **flat string** built by joining all segment texts. If segments are **plain ASR text without `Speaker A:` / `Speaker B:`** labels (or without other role cues), the model has **no explicit notion of “who said what.”** It can only compress surface wording, so it may miss **accountability** (who owns an action) and produce a **less precise** summary than the same conversation with diarized, speaker-prefixed segments. This is a **model + input representation** limitation, not only a bug in the UI.  
- **User-visible behavior:** The “AI Summary” box still shows a fluent paragraph, but it may not distinguish speakers or may merge their points—motivating the **WhisperX + diarization** improvement in §3.4.

#### Failure 2: `SmolLM2-360M-Instruct` returns 404 — model not deployed on HF Inference Providers

- **What happened:** Clicking “Get action items” returned `502 Bad Gateway`. The Django server log showed `Bad Gateway: /api/action-items/` with no traceback, meaning the exception was being swallowed. Manually calling `InferenceClient.chat_completion(model="HuggingFaceTB/SmolLM2-360M-Instruct", ...)` returned `404 Client Error: Not Found for url: https://router.huggingface.co/hf-inference/models/HuggingFaceTB/SmolLM2-360M-Instruct/v1/chat/completions`.
- **Why:** `HuggingFaceTB/SmolLM2-360M-Instruct` was the default model in `api_action_items`. It is **not deployed** on the HF Inference Providers free tier — the router has no running replica for it, so every request returns 404. The broad `except Exception as e` block caught the `HfHubHTTPError` and returned 502 with an empty `detail`, hiding the real cause.
- **Fix:** Switched the default model to `Qwen/Qwen2.5-7B-Instruct`, which is reliably deployed on HF Inference Providers and produces high-quality chat completions. Also added `logger.exception()` to the catch-all block so future failures print a full traceback in the Django console instead of silently returning 502.
- **User-visible behavior after fix:** “Get action items” returns a formatted bullet list within ~2 seconds. Default model can be changed with **`HF_ACTION_ITEMS_MODEL`** in `.env`.


---

### Step 3.4: WhisperX with speaker diarization

#### Problem (before)

Plain ASR (e.g. running **Whisper-style transcription only** without diarization) gives **text** but not **who spoke when**. For coaching and standups, “who said what” matters. A single block of text (or many tiny segments without labels) makes downstream summarization and review **harder to scan** and does not match how EchoLabs displays **multi-turn** transcripts elsewhere (seed data uses `Speaker A:` / `Speaker B:` lines).

#### Change (after)

The integrated pipeline in **`conversations/transcribe.py`** uses **WhisperX**:

1. **ASR** with a configurable Whisper checkpoint (`WHISPER_MODEL`, default `base`).  
2. **Forced alignment** for better word/segment timing.  
3. **Speaker diarization** via pyannote (requires **`HF_TOKEN`** and accepting the model terms on Hugging Face).  
4. **Speaker assignment** into segments; labels are normalized to **`Speaker A`**, **`Speaker B`**, … in stored segment text.

So each `TranscriptSegment` row can read like: `Speaker A: …` / `Speaker B: …`, consistent with manually seeded transcripts.

#### Before / after (same audio as **TC1**)

| Version | Content |
|--------|---------|
| **Before improvement** | Plain transcript **without** speaker labels — **TC1** blockquote in §3.2 (one joined paragraph). |
| **After improvement (WhisperX + diarization)** | Full transcript with speaker labels as produced after alignment and `assign_word_speakers` (pyannote may label clusters as Speaker A–E depending on the clip). |

**After — diarized transcript (example):**

```
Speaker E: Hello everyone, thank you guys for coming to our weekly student success meeting and let's just get started.

Speaker E: So I have our list of chronically absent students here and I've been noticing a troubling trend.

Speaker E: A lot of students are skipping on Fridays.

Speaker E: Does anyone have any idea what's going on?

Speaker D: I've heard some of my mentees talking about how it's really hard to get out of bed on Fridays.

Speaker D: It might be good if we did something like a pancake breakfast to encourage them to come.

Speaker D: I think that's a great idea.

Speaker D: Let's try that next week.

Speaker C: It might also be because a lot of students have been getting sick now that it's getting colder outside.

Speaker C: I've had a number of students come by my office with symptoms like sniffling and coughing.

Speaker C: We should put up posters with tips for not getting sick since it's almost flu season, like, you know, wash your hands after the bathroom, stuff like that.

Speaker E: I think that's a good idea and it'll be a good reminder for the teachers as well.

Speaker E: So one other thing I wanted to talk about, there's a student I've noticed here, John Smith.

Speaker E: He's missed seven days already and it's only November.

Speaker E: Does anyone have an idea what's going on with him?

Speaker D: I might be able to fill in the gaps there.

Speaker D: I talked to John today and he's really stressed out.

Speaker D: He's been dealing with helping his parents take care of his younger siblings during the day.

Speaker D: It might actually be a good idea if he spoke to the guidance counselor a little bit.

Speaker A: I can talk to John today if you want to send him to my office after you meet with him.

Speaker A: It's a lot to deal with for middle schooler.

Speaker B: Great thanks and I can help out with the family's childcare needs.

Speaker B: I'll look for some free or low-cost resources in the community to share with John and he can share them with his family.

Speaker E: Great, awesome really good ideas here today.

Speaker E: Thanks for coming and if no one has anything else I think we can wrap up.
```

**Summary:** Speaker E has noticed that a lot of students are skipping on Fridays. Speaker D suggests a pancake breakfast to encourage them to come. Speaker C suggests putting up posters with flu-related tips. Speaker E wants to talk to John Smith, who has been absent seven days in a row and it's only November. Speaker A will help John with his childcare needs.

**Comparison:** same audio; only the diarization and labeling pipeline changed (before = plain paragraph; after = labeled turns above).

#### Why it helped

- **Readability:** Users can skim by speaker in the conversation detail UI.  
- **Downstream AI:** With **`Speaker A:` / `Speaker B:`** in each segment, the **same** BART summarizer receives clearer **turn structure** in the text, which reduces the **generic, undifferentiated** summaries described in **Failure 1** on the same recording **before** vs **after** diarization.  
- **Alignment with product:** EchoLabs is conversation-centric; diarized segments match that mental model.

#### Tradeoffs

- **Setup:** Requires `HF_TOKEN` for pyannote; first run downloads weights.  
- **Latency / compute:** Diarization adds work versus ASR-only; acceptable for short clips under the configured **max duration** / **max file size** caps.

---

