# RAG Pipeline — Echolabs

## Files

| File | Description |
|------|-------------|
| `rag_system.ipynb` | Full RAG implementation: knowledge base, chunking, embeddings, retrieval, generation, experiments (Parts 1–3) |
| `rag_analysis.md` | Evaluation tables, embedding/chunking comparisons, failure analysis, system design reflection (Parts 2–4) |
| `requirements.txt` | Python dependencies |

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate          # Windows

# 2. Install dependencies
pip install -r requirements.txt
```

## Running the notebook

```bash
# Launch Jupyter
jupyter notebook rag_system.ipynb

# Or use JupyterLab
jupyter lab rag_system.ipynb
```

Run cells **top to bottom**. The notebook will:

1. Download the `knkarthick/dialogsum` dataset from Hugging Face (automatic, no login needed).
2. Download three embedding models (`multi-qa-MiniLM-L6-cos-v1`, `multi-qa-mpnet-base-cos-v1`, `BAAI/bge-large-en-v1.5`) and one generation model (`google/flan-t5-base`). First run downloads ~2 GB of weights; subsequent runs use the cache.
3. Build chunks, embed them, run 45 retrieval+generation experiments (3 embeddings × 3 chunking strategies × 5 queries), and display results.
4. Run a data scaling experiment comparing 32 vs 882 paragraphs (~6–7 min).
5. Run failure analysis with before/after prompt comparison.

## Notes

- **GPU is optional.** All models run on CPU (slower but functional). If CUDA is available it is used automatically.
- **Model weights** are cached in `~/.cache/huggingface/hub/`. To free disk space later, delete that directory.
- The `rag_test.ipynb` file is the original notebook; `rag_system.ipynb` is the submission copy.
