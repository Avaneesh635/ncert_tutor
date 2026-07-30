# Worklog

## AI tools used
- **Qwen** — pair‑programming partner for architecture, debugging, and the retrieval
  diagnostics (`diag*.py`, `check.py`).
- **Google Gemini** (`gemini-3.6-flash`) — the tutor LLM, via the OpenAI‑compatible endpoint.

## Key decisions (chronological)
1. **OpenAI → Gemini.** The starter used OpenAI's *Responses* API; Gemini's compatibility
   endpoint serves the standard `chat.completions` API, so the call was switched and the
   `base_url`/model pointed at Gemini. Chosen for its free tier, large context window, and
   strong STEM reasoning.
2. **Secrets in `backend/.env`.** The starter's `load_dotenv(Path(__file__).with_name(".env"))`
   loads `backend/.env` specifically, so the key lives there (not the repo root).
3. **Built the RAG layer.** `pypdf` extraction → 800‑char chunks → `sentence-transformers`
   embeddings → persistent ChromaDB index; retrieval feeds a grounded, citation‑bearing prompt.
4. **Added a cross‑encoder reranker** (`ms-marco-MiniLM`) over a wide first‑stage fetch for
   precision.
5. **Diagnosed the coordination miss.** `diag2`/`diag3` proved the chapter text exists in
   `chemistry_part_1.pdf` but ranks in the bi‑encoder long tail; the source pages carry
   font‑encoding artifacts. Tried TOP_K↑, reranker, over‑fetch 4→100, a stronger embedder
   (mpnet), and PDF cleaning — none surfaced it. Settled on a correct general‑knowledge
   fallback and documented it as a limitation.
6. **Empty‑completion guard.** A Gemini model returned blank content for a prediction query
   and an edge case; added a fallback regeneration + default refusal so the tutor never
   answers blank.
7. **Scope‑first prompt.** Caught an out‑of‑scope Biology question being answered from general
   knowledge; restructured the system prompt to check scope *before* grounding.
8. **Extended the eval set 8 → 14** with harder probes (anode‑sign trap, SN1/SN2, Nernst
   location, a numeric, extra out‑of‑scope cases) to stress‑test grounding and the guardrail.
9. **Single‑file chat UI.** Added `frontend/index.html` served by FastAPI at `/` (same origin,
   no CORS juggling); renders LaTeX/tables/citation chips and keeps multi‑turn history
   client‑side, exercising the `messages` contract.

## Outcome
11/14 in‑scope answers correct and cited; coordination correct via fallback (uncited);
all 3 out‑of‑scope refused; no empty answers. See `evals/reports/visible_eval_*.json`
and the per‑run scorecard in `result.md`.
