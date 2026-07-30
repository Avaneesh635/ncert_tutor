# NCERT Tutor — ask the books, get the page

> Ask it *Lenz's Law* and it doesn't just explain it — it tells you **which page of
> Physics Part 1** the explanation came from. Ask it *photosynthesis* and it politely
> declines, because that's Biology, not your syllabus. That grounding-and-guardrail pairing,
> on the official Class 12 textbooks, is the whole project.

A retrieval‑augmented tutor for **CBSE Class 12 Physics, Chemistry, and Mathematics**.
Every in‑scope answer is built from passages pulled out of the six NCERT PDFs and tagged with
its source page; every off‑syllabus question gets a one‑line redirect instead of a lecture.
It ships with a chat interface, a 14‑case evaluation suite, and a measured iteration log.

---

## What it actually does

- **Grounds, then cites.** A question goes to a two‑stage retriever (a fast bi‑encoder that
  casts a wide net, then a cross‑encoder that re‑reads each candidate against the question and
  keeps the best). The winning passages are handed to the model inside a *grounded* prompt, and
  the model is instructed to attach a `[book: p.X]` tag to every key claim.
- **Knows its lane.** Before grounding anything, the model runs a scope check. Biology, history,
  programming, current affairs, match predictions — all redirected to the PCM syllabus in a
  single sentence, with no retrieved context quoted and no general‑knowledge answer smuggled in.
- **Never answers blank.** If the model ever returns an empty completion (it will, on a
  safety‑filtered prediction‑style query), the agent regenerates once in general‑knowledge mode
  and, as a last resort, returns a default refusal. An empty bubble is impossible by
  construction.
- **Remembers the thread.** The chat UI keeps the full conversation client‑side and sends it
  every turn, so follow‑ups build on what came before — the first real exercise of the
  multi‑message `POST /chat` contract.
- **Renders like a textbook, not a log.** Answers come back as Markdown with typeset maths
  (KaTeX), styled comparison tables, and the page citations turned into small interactive chips.

## How an answer is made

```
 you type a question
        │
        ▼
  frontend/index.html  ──fetch("/chat", { messages: [...] })──┐  same origin,
        ▲                                                     │  no CORS juggling
        │  cited answer, rendered                             ▼
        │                                          backend/main.py
        │                                          POST /chat  →  GET /  (the UI)
        │                                                     │
        │                                                     ▼
        │                                          backend/agent.py  (StarterAgent)
        │                                             │ 1. rag.retrieve(question)
        │                                             ▼
        │                                          backend/rag.py
        │                                          clean() the PDF text
        │                                          chunk (800 chars)
        │                                          embed  →  all-mpnet-base-v2 (768-d)
        │                                          over-fetch 100 from ChromaDB
        │                                          re-rank  →  ms-marco cross-encoder
        │                                          keep top-k
        │                                             │
        │                                             ▼
        │                              grounded prompt + scope-first SYSTEM_PROMPT
        │                                             │
        │                                             ▼
        │                              Gemini (OpenAI-compatible /chat/completions)
        │                              + empty-completion fallback
        │                                             │
        └──────────────────  { "answer": "...", "model": "..." }
```

## Model policy — why Gemini, and the tradeoffs

The starter template defaulted to OpenAI's *Responses* API. This build runs on **Google
Gemini** (currently `gemini-3.6-flash`, set via `self.model` in `backend/agent.py`) through
Gemini's **OpenAI‑compatible endpoint**.

**Why the switch:**
- **Free tier that's enough.** A free AI Studio key covers the whole project — ingest, the eval
  suite, the grader's run, the live demo — with no billing. The OpenAI path the starter assumed
  needs a paid key, which is the wrong default for a student submission.
- **Context headroom.** Long textbook passages fit comfortably, which is what grounding demands.
- **STEM that holds up.** Derivations, reaction mechanisms, and physics/maths numericals come
  back correct and cited (see *Evaluation*).
- **Drop‑in, mostly.** Because Gemini speaks the OpenAI wire format, the change was a `base_url`
  plus a model name — *except* the starter's newer Responses API, which Gemini's compatibility
  layer doesn't serve. That call was rewritten to the standard `chat.completions` API.

**The honest costs:**
- **Rate limits.** The free tier throttles bursts, so the eval harness runs cases *sequentially*
  and the SDK retries (`max_retries=5`) absorb the occasional `429`.
- **Empty completions.** Some prediction‑style prompts return no content; the fallback guard
  above turns that from a visible failure into a graceful refusal.
- **Recall is only as good as the embeddings and the source text.** See *Limitations* — one
  chapter sits in the retriever's long tail, and the cause is diagnosed, not hand‑waved.

## Setup (from a clean machine)

Needs Python 3.10+ and a Google AI Studio key
([aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)).

```bash
# 1. dependencies
pip install -r requirements.txt

# 2. your key — the app loads backend/.env specifically (not the repo root)
echo 'GEMINI_API_KEY=AIza...your_key' > backend/.env

# 3. the six NCERT Class 12 PDFs listed in data/manifest.json
#    download from https://ncert.nic.in/textbook.php into data/raw/
#    using the suggested names (physics_part_1.pdf, chemistry_part_2.pdf, …)

# 4. build the vector index once (~1–2 min; downloads the embedding model on first run)
python -m backend.ingest
```

## Run it

```bash
uvicorn backend.main:app --reload
```

Then open the **chat UI** at the root — not `/docs`:

```
http://127.0.0.1:8000/
```

`/docs` (the API reference) and `GET /health` (the heartbeat) still work as before. A raw call:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"State and explain Lenz'\''s Law."}]}'
```

## The chat interface

`frontend/index.html` is a single self‑contained file — no build step, no `node_modules` —
served by FastAPI at `/` so the page and the API share one origin (which is why there's no
CORS config to get wrong; a permissive `CORSMiddleware` is kept only as a safety net). It
renders the model's Markdown and LaTeX, turns each `[book: p.X]` into a citation chip, shows a
typing indicator while Gemini thinks, and holds the conversation history in the browser so a
follow‑up like *"now what's the negative sign for?"* stays on topic. It degrades gracefully if a
CDN is unreachable (raw LaTeX in `<code>`, chips still rendered).

## Evaluation

The provided 8‑case set was **deliberately hardened to 14** with the probes a naive set misses:
a series‑resistors numeric, an *anode‑sign trap* (the anode is negative in a galvanic cell but
**positive** in an electrolytic one), an SN1/SN2 mechanism comparison, a Nernst‑equation
"which chapter" lookup, and two extra out‑of‑scope questions.

**Shipped run — `gemini-3.6-flash`, 14/14 behaving as designed:**

| In‑scope (11) | Out‑of‑scope (3) | Wrong | Empty |
| :--: | :--: | :--: | :--: |
| 10 cited + 1 documented fallback | 3 clean refusals | 0 | 0 |

The single fallback is *Coordination Compounds* — answered correctly from general knowledge and
explicitly flagged as not located in the retrieved pages (the known retrieval gap, below). It is
counted as correct, never as a citation.

The four saved reports also capture the **iteration arc**, which is the more interesting story:
the set grew 8 → 14; a model swap to `gemini-2.5-flash` surfaced a guardrail *leak* (the Biology
probe got answered instead of refused); the scope‑first prompt closed it; the final run on
`gemini-3.6-flash` is clean. The full per‑case, per‑run scorecard with verifiable evidence
strings lives in **[`result.md`](result.md)** — kept separate so this README states the headline
and `result.md` holds the proof, and the two can't drift.

Reproduce a report yourself:

```bash
# Terminal 1:  uvicorn backend.main:app --reload
# Terminal 2:
python -m evals.run_evals     # → evals/reports/visible_eval_<timestamp>.json
python read_report.py         # pretty-prints the latest (CITED / NO-CITE / REFUSE per case)
```

## Design decisions (the *why*)

- **`chat.completions`, not the Responses API.** Gemini's compatibility endpoint serves the
  standard chat API; the starter's Responses‑API call had to be rewritten. The legacy serializer
  for it is left in the tree, type‑clean and documented as dormant.
- **Secrets in `backend/.env`.** The starter's `load_dotenv(Path(__file__).with_name(".env"))`
  resolves to `backend/.env`, so that's where the key lives — and only there.
- **Two‑stage retrieval.** A bi‑encoder alone over‑scores the wrong chemistry chapter for some
  queries; over‑fetching 100 and re‑ranking with a cross‑encoder is materially more precise, and
  the rerank is query‑time so it costs no re‑ingest.
- **Light PDF cleaning.** The NCERT PDFs leak header junk (`C:\…Unit‑X.pmd …`) and break words
  across lines; `clean()` strips and re‑joins so embeddings reflect content, not artifacts.
- **Scope‑first prompt.** The model decides in/out‑of‑scope *before* it ever sees the grounding
  block, so the "answer from general knowledge" permission applies only to in‑scope questions —
  this is what stopped the Biology leak.
- **Same‑origin UI.** Serving the page from FastAPI removes an entire class of CORS and
  port‑mismatch bugs for zero downside.

## Project structure

```
backend/
  main.py        FastAPI app — GET / (UI), POST /chat, GET /health, CORS net
  agent.py       StarterAgent — retrieve → grounded prompt → Gemini (+ fallback)
  rag.py         ingest() + retrieve() — clean, chunk, embed, ChromaDB, cross-encoder rerank
  constants.py   scope-first SYSTEM_PROMPT + RAG settings (embedder, top-k, chunk size)
  types.py       ChatRequest / ChatResponse contracts
  ingest.py      CLI entry — python -m backend.ingest
frontend/
  index.html     single-file chat UI (served at /)
data/
  manifest.json  the 6 required NCERT books + suggested filenames
  raw/           the PDFs (gitignored — download per manifest)
evals/
  run_evals.py   HTTP harness — preflights /health, runs cases sequentially
  prompts.json   the 14-case set
  reports/       generated visible_eval_*.json (committed as evidence)
result.md        per-run, per-case scorecard behind the headline numbers
chroma_db/       persistent vector index (gitignored — rebuilt on setup)
```

## Limitations & future work

- **Coordination Compounds retrieval.** The chapter text *is* in the source — `chemistry_part_1.pdf`,
  roughly pp. 243–262, verified independently with `pypdf` and `pdfplumber` (so it is **not** an
  extraction gap). But the embedder ranks those pages in the long tail for coordination queries,
  below unrelated organic‑chemistry pages, so they never reach the reranker; and the pages carry
  font‑encoding artifacts (e.g. `Exa l 2 4Example 12.4`) that defeat both cleaning and embedding.
  **Tried:** cross‑encoder reranker, over‑fetch 4 → 100, a stronger embedder
  (`all-MiniLM-L6-v2` → `all-mpnet-base-v2`, 384 → 768 dims), and PDF‑text cleaning — none
  surfaced it. **Result:** a correct, clearly‑labelled, *uncited* answer — never a wrong or
  fabricated one. **Next:** OCR‑level extraction, hybrid BM25 + vector search, HyDE query
  expansion, or a chapter‑aware router.
- **Scope guard is prompt‑based and model‑sensitive.** The same out‑of‑scope Biology question is
  refused on `flash-latest` and `3.6-flash` but leaked on `2.5-flash` (captured in `result.md`),
  which is exactly why a lightweight intent *classifier* before retrieval is the right next step
  rather than relying on the model's judgement alone.
- **Fixed‑window chunking.** Chunks are 800‑char windows, not structure‑aware (chapter/section)
  chunks that keep a definition, its formula, and its worked example together. A hierarchical
  semantic chunker was evaluated but not adopted, to avoid regressing a working pipeline; it is
  the natural follow‑on.

## Security

The API key exists only in `backend/.env`, which is gitignored. No secrets, source PDFs,
virtualenvs, or the vector index are committed — the grader rebuilds the index from the setup
steps above and `data/manifest.json`.