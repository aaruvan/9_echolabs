# RAG Analysis — Echolabs

## Part 2: System Experiments

### Step 2.2 — Evaluation Table

Scoring rubric (1–5):

| Score | Retrieved Context Quality | Answer Quality |
|-------|--------------------------|----------------|
| 5 | Highly relevant, no noise | Accurate, complete, well-phrased |
| 4 | Mostly relevant, minor noise | Mostly correct, minor gaps |
| 3 | Partially relevant (≥1 good chunk) | Partially correct |
| 2 | Mostly irrelevant | Vague or mostly wrong |
| 1 | Completely off-topic | Hallucinated / no answer |

#### Summary — averages per configuration (over 5 queries)

| Embedding Model | Chunking Strategy | Avg Context Quality | Avg Answer Quality | Avg Latency (s) |
|----------------|-------------------|--------------------|--------------------|-----------------|
| small (384d) | fixed_length | 2.60 | 1.80 | 4.76 |
| small (384d) | overlapping_paragraph | 2.80 | 1.40 | 2.04 |
| small (384d) | hybrid_strategic | 1.60 | 1.00 | 1.76 |
| medium (768d) | fixed_length | 2.40 | 1.40 | 3.54 |
| medium (768d) | overlapping_paragraph | 2.60 | 1.40 | 1.56 |
| medium (768d) | hybrid_strategic | 1.60 | 1.00 | 1.46 |
| large (1024d) | fixed_length | 3.40 | 2.60 | 4.76 |
| large (1024d) | overlapping_paragraph | 3.20 | 1.60 | 1.66 |
| large (1024d) | hybrid_strategic | 2.00 | 1.00 | 1.56 |

Full per-query scores and retrieved chunks are in `rag_system.ipynb` (Step 2.2 output cells).

---

### Step 2.3 — Compare Embedding Models

| Embedding Model | Avg Context Quality | Avg Answer Quality | Avg Latency (s) |
|----------------|-------------------|------------------|----------------|
| Small (384d / multi-qa-MiniLM-L6-cos-v1) | 2.33 | 1.47 | 3.37 |
| Medium (768d / multi-qa-mpnet-base-cos-v1) | 2.20 | 1.27 | 2.28 |
| Large (1024d / BAAI/bge-large-en-v1.5) | 2.87 | 1.73 | 2.66 |

**Small (384d):** Similarity scores were consistently lower and the top-3 chunks often contained off-topic dialogues. The 384-dimensional space is too compressed for nuanced dialogue semantics, so similar-sounding surface words like "help" and "please" pull irrelevant chunks to the top.

**Medium (768d):** Surprisingly, medium performed *worse* than small on context quality (2.20 vs 2.33). MPNet's larger embedding space did not translate to better retrieval on dialogue-format text — for Q2 and Q5 it ranked the correct chunk lower than the small model did, suggesting multi-qa-mpnet-base-cos-v1 is less well-calibrated for short conversational snippets than MiniLM.

**Large (1024d):** Best retrieval scores overall. BGE-large is instruction-tuned for retrieval and its 1024-d embeddings separate topic clusters more cleanly. The large model's advantage was clearest in fixed_length configs (avg context quality 3.4) where tight chunk boundaries amplified its discriminative power.

**Did larger always perform better?** No. Medium underperformed small on both context quality (2.20 vs 2.33) and answer quality (1.27 vs 1.47), making it the weakest embedding model overall. Large won clearly on fixed_length chunking but showed score inflation on hybrid_strategic — assigning high cosine scores to large mixed-topic sections without improving answer usefulness.

---

### Step 2.4 — Compare Chunking Strategies

| Chunking Strategy | Avg Context Quality | Avg Answer Quality | Avg Latency (s) | Num Chunks |
|------------------|-------------------|------------------|----------------|------------|
| Fixed Length | 2.80 | 1.93 | 4.76 | 33 |
| Overlapping Paragraph | 2.87 | 1.53 | 2.00 | 31 |
| Hybrid Strategic | 1.73 | 1.00 | 1.56 | 11 |

**Which strategy worked better?** Fixed-length produced the best answer quality (1.93), while overlapping paragraph edged ahead on context quality (2.87 vs 2.80). Hybrid strategic was the weakest by a significant margin — answer quality of 1.0 across all embedding models.

**Why?**
- **Fixed-length** (~134 words) creates tight semantic units — each chunk typically covers one dialogue — making cosine scores more meaningful.
- **Overlapping paragraph** was competitive, particularly for Q4 (evening plans) where it correctly surfaced the cinema dialogue. The 50% overlap helped when relevant turns spanned paragraph boundaries. However, overlap also created a contamination problem: Dialogue 27 (bus directions) was consistently retrieved alongside Dialogue 28 (resignation) because they are adjacent paragraphs.
- **Hybrid** had two failure modes: (1) semantic dilution — a section with a doctor visit, keys dialogue, and vaccination scene produces a blended embedding that weakly matches any single topic; (2) answer confusion — even when the correct section was retrieved, flan-t5-base read the *wrong* dialogue within that section.

**How did chunking affect final answers?**

| Strategy | Best Answer Produced | Avg Answer Quality |
|----------|--------------------|-------------------|
| Fixed Length | *"There's a baseball game on television tonight"* — specific, accurate | 1.93 |
| Overlapping | *"I'd rather not spend a lot of money…"* — correct and contextual | 1.53 |
| Hybrid | *"is the best one?"*, *"beautiful"*, *"where the visa office is?"* — hallucinations | 1.00 |

Fixed-length's shorter, semantically purer chunks gave flan-t5-base a much cleaner signal to generate from.

---

### Step 2.5 — Data Scaling Experiment

**Query:** *"How does someone handle quitting or leaving a job?"*
**Best configuration:** Overlapping Paragraph + Large (1024d BGE)

| Scale | Paragraphs | Chunks | Avg Top-3 Sim | Top-1 Sim | Latency (s) |
|-------|-----------|--------|--------------|-----------|-------------|
| Baseline | 32 | 31 | 0.6276 | 0.6693 | 0.097 |
| Extended | 882 | 881 | 0.6775 | 0.6847 | 0.079 |

**How does dataset size affect retrieval quality?** Quality improved — both avg top-3 similarity (0.6276 → 0.6775) and top-1 similarity (0.6693 → 0.6847) increased. The extended dataset contained more and better resignation dialogues, surfacing three genuinely relevant chunks instead of one correct chunk plus contamination.

**How does dataset size affect noise?** Noise decreased. In the baseline, rank 2 was a bus/directions dialogue contaminated via overlap adjacency. In the extended set, this was replaced by genuinely relevant resignation/workplace dialogues because the BGE model had enough truly relevant options to fill all three top-3 slots.

**Key takeaways:**
- More data improved both retrieval quality and reduced noise for this topic.
- The large BGE model scaled efficiently — latency actually decreased slightly (0.097s → 0.079s) from baseline to extended.

---

## Part 3: Failure Analysis & Improvement

### Step 3.1 — Failure Cases

**F1 (hybrid strategic, large embedding, Q4 — evening/leisure):** Cosine search ranked the cinema dialogue first, so retrieval found on-topic text. The answer was still wrong: flan-t5 returned a short fragment tied to a different movie dialogue in the top-3, not the cinema chunk.

**F2 (hybrid, large, Q3 — computer/electronics):** The top block included the computer store dialogue, but the model answered with an unrelated line (e.g. about a visa office). Hybrid sections pack several dialogues into one chunk and one vector, so the generator copies text from the wrong conversation even when similarity scores look fine.

**F3 (overlapping paragraph, Q2 — resignation/workplace):** Overlap joins neighbouring dialogues. A bus/directions scene sat next to the resignation dialogue in the data, so one chunk contained both and scored well enough to land in top results. That adds noise next to the real resignation chunk.

### Step 3.2 — Root Cause Analysis

| Failure | Root Cause |
|---------|-----------|
| F1 | **Chunking:** Hybrid mixes topics in one section; the seq2seq model fails to stay on the best passage. Embedding put a good chunk first; the query is clear. |
| F2 | **Chunking:** Same hybrid structure — big mixed sections get high scores; the generator grabs an irrelevant sentence from the blob. Embedding plays a smaller role than chunk shape. |
| F3 | **Chunking (overlap):** Unrelated neighbours share a vector. Embeddings just reflect what got concatenated; rephrasing the query would not remove the neighbour effect. |

### Step 3.3 — System Improvement

**Fix applied:** Improved prompt template (same flan-t5-base, same large embedding, same hybrid chunking, same top_k=3). The only change is how chunks are described in the prompt: the improved version states that contexts are ordered by relevance and prints the similarity score next to each context header so the model can lean on the top block.

**Before vs After:**

| Case | Query | Original Answer | Improved Answer |
|------|-------|----------------|-----------------|
| F1 evening | What do people plan for entertainment this evening? | *"is the best one?"* | *"I'm tired of watching television. Let's go to cinema tonight…"* (quotes correct cinema dialogue) |
| F2 computer | What advice is given about buying a computer? | *"Excuse me, do you know where the visa office is?"* | *"I'll get a 15-inch monitor…"* (on-topic, though still a raw fragment) |

The prompt change helped F1 significantly — the model now reads from the highest-scored chunk instead of a random passage. F2 improved but is still not a clean summary, confirming that hybrid chunking is a harder problem than prompt phrasing alone can fix.

> Note: Prompt changes will not fix F3-style overlap contamination; that would require different chunking or post-retrieval filtering.

---

## Part 4: System Design Reflection

### Step 4.1: Cost Awareness (15 pts)

For our RAG stack (sentence-transformers embeddings + cosine search + `flan-t5-base` generation), the main cost drivers are:

| Factor | Why it impacts cost |
|--------|---------------------|
| **Embedding model size** | Larger models (768d → 1024d) use more GPU/CPU time per query and per offline index build, and need more RAM/VRAM. Index storage grows linearly with embedding dimension × number of chunks. |
| **Chunk size / chunk count** | Smaller chunks mean more vectors in the store: more memory, slower brute-force similarity, and higher one-time embedding cost when rebuilding the index. Larger chunks mean fewer vectors but longer encode/decode per chunk and more tokens passed to the LLM. |
| **Top-k retrieval** | Each increment of *k* adds more text into the prompt → more input tokens to the generator (dominant cost if using a paid API) and longer generation time. It does not change embedding cost per query much but increases downstream cost and latency. |

**What dominates in practice:** For self-hosted inference, generation (seq2seq forward passes) dominates latency and GPU seconds per request; embedding a short query is cheap compared to generating 60+ new tokens. For hosted APIs billed by token, top-k and chunk length directly inflate prompt size and dominate variable cost. Embedding dimension dominates index disk/RAM and batch-reindexing cost.

---

### Step 4.2: RAG vs Alternatives (15 pts)

| Approach | When to Use |
|----------|-------------|
| **RAG** | Knowledge changes often (new dialogues, FAQs, docs); you need citations / grounded answers from a specific corpus; limited budget for retraining; privacy requires data stay in your vector store. Best when factual recall from documents matters more than stylistic imitation. |
| **Fine-tuning** | Stable task with enough labeled or high-quality examples; the model must internalize a style, format, or domain phrasing; latency and simplicity matter (no retrieval step). Weak fit when facts change weekly — weights go stale unless you retrain. |
| **Pure prompting** | Small knowledge fits in context, or the task is general reasoning with no private corpus; fastest to ship; no index to maintain. Breaks down when context exceeds model limits, when you cannot trust the model to recall long-tail facts, or when you must enforce only organization-specific content. |

**For Echolabs:** RAG fits wearable conversation transcripts + coaching content that grows per user: we retrieve relevant snippets, then summarize or answer with `flan-t5-base`. Fine-tuning could supplement tone or output format; pure prompting alone is risky for large, user-specific histories.

---

### Step 4.3: System Design (20 pts)

#### Scaling to ~10,000 users / day

Assume 10–20% of DAU issues RAG queries → 1–2K RAG queries/day (~1–2 QPS average, higher at peaks).

**Architecture:**
1. **Stateless web tier** (Django or API workers) — auth, rate limits, validate query length.
2. **Embedding service** — load one sentence-transformer (e.g. BGE-large) in a GPU worker pool; cache query embeddings for identical repeated queries (short TTL).
3. **Vector store** — in-memory or on-disk FAISS / pgvector; for 10K DAU and modest corpus size, a single shard is enough.
4. **Generation workers** — `flan-t5-base` on GPU or CPU with a queue (Celery / Redis) so spikes do not block the web server; strict max prompt tokens and timeout.
5. **Observability** — log latency percentiles, retrieval scores, and empty/low-confidence results to tune top-k and prompts.

**What to optimize first:**
- Top-k and chunking — reduce prompt tokens without hurting recall.
- Batch / async — offload generation from the request thread.
- Caching — cache final answers for (query hash, corpus version) where privacy allows.
- Smaller embedding model for a "fast lane" if we add routing.

#### System Diagram

```
ONLINE (per request):

  User --> Query --> Embedding Model --> Query Vector --> Vector Store --> Retrieved Context --> LLM --> Response
                                                              ^              (top-k chunks)    (flan-t5-base)
                                                              |
OFFLINE (index build):                                        |
                                                              |
  Knowledge Base --> Chunking --> Embedding Model --> Chunk Vectors
```

**Step-by-step:**

**Offline (runs once or when data changes):**
1. Knowledge base (e.g. DialogSum dialogues) is split into chunks using one of the three chunking strategies.
2. Each chunk is encoded by the embedding model (e.g. BGE-large 1024d) to produce chunk vectors.
3. Chunk vectors are stored in the vector store (in-memory cosine similarity index).

**Online (per user request):**
1. User submits a natural-language query.
2. The same embedding model encodes the query into a query vector.
3. Vector store compares the query vector against precomputed chunk vectors using cosine similarity and returns the top-k most relevant chunks.
4. Prompt assembly combines a system instruction, the retrieved context chunks, and the user query.
5. LLM (`flan-t5-base`) generates the final answer from the assembled prompt.
6. Response is returned to the user.
