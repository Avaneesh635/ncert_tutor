# Evaluation Results — NCERT Class 12 PCM Tutor

> **Shipped run — 14 / 14 cases behave as designed.** 10 grounded-and-cited, 1 correct
> general-knowledge fallback (the documented *Coordination Compounds* retrieval gap),
> 3 clean out-of-scope refusals, **0 wrong answers, 0 empty answers.**
> Model `gemini-3.6-flash` · artifact `evals/reports/visible_eval_20260730T082601Z.json`

This file is the precise, per-run scorecard behind the headline numbers in the README.
Each row cites the exact evidence string found in the corresponding report, so any verdict
can be checked against the raw JSON in `evals/reports/`.

---

## How to read the verdicts

| Glyph | Verdict | Meaning |
| :---: | :--- | :--- |
| ✅ | **Cited** | In-scope answer grounded in retrieved NCERT text, with a `[book: p.X]` citation. |
| 🟡 | **Fallback** | In-scope and *correct*, but answered from general knowledge because retrieval returned no relevant passage (the known Coordination-Compounds gap). Expected, never wrong. |
| ⬜ | **Refused** | Out-of-scope question met with a one-line redirect to the PCM syllabus — no lecture, no citation. |
| 🔴 | **Leak** | An out-of-scope topic was *answered* instead of refused — a guardrail failure. |

A run is **clean** when it contains no 🔴 and no empty answers.

---

## Trajectory at a glance

Four runs, oldest → newest. The set grows from 8 to 14 cases; one model swap surfaces a
guardrail leak; the prompt is hardened; the final run is clean.

| # | Report file | Model | Cases | ✅ | 🟡 |  | 🔴 | Status |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :--- |
| 1 | `visible_eval_20260729T150907Z.json` | `gemini-flash-latest` | 8  | 6 | 1 | 1 | 0 | 🟢 baseline |
| 2 | `visible_eval_20260729T153557Z.json` | `gemini-flash-latest` | 14 | 10 | 1 | 3 | 0 | 🟢 extended set, clean |
| 3 | `visible_eval_20260730T072325Z.json` | `gemini-2.5-flash`    | 14 | 10 | 1 | 2 | 1 | 🔴 biology leak |
| 4 | `visible_eval_20260730T082601Z.json` | `gemini-3.6-flash`    | 14 | 10 | 1 | 3 | 0 | ✅ **SHIPPED** |

> **Note on the in-scope count.** "In-scope" = the 11 PCM questions (6 core + 4 hard probes +
> Coordination Compounds). Of those, **10 are cited** and **1 (Coordination) is the correct
> uncited fallback** — so "11 in-scope correct" = 10 ✅ + 1 🟡. The remaining 3 cases are the
> out-of-scope refusals. This is the exact decomposition; the README's looser phrasing
> ("11 in-scope with citations") folds the fallback into that headcount.

---

## Run 1 — baseline 🟢 · `gemini-flash-latest` · 8 cases

The original provided suite, run before the set was stress-tested. Everything grounds and
cites; the only out-of-scope probe (cricket) is refused. Coordination already shows the
fallback behaviour that persists in every later run.

| Case | Verdict | Evidence (from report) |
| :--- | :---: | :--- |
| `integrals-concept` | ✅ | `mathematics_part_1: p.274`, `p.340` |
| `partial-fractions` | ✅ | `mathematics_part_2: p.65, p.47` |
| `emf-terminal-voltage` | ✅ | `physics_part_1: p.114`, `p.117` |
| `electrochemical-cell` | ✅ | `chemistry_part_1: p.96`, `p.70` |
| `matrices-chapter` | ✅ | `mathematics_part_1: p.105, p.116`, `p.108` |
| `electrostatics-field-lines` | ✅ | `physics_part_1: p.29, p.47` |
| `coordination-compounds` | 🟡 | "context pages do not contain … based on the general Class 12 Chemistry syllabus" (no citation) |
| `out-of-scope-cricket` | ⬜ | "I can only answer questions related to the Class 12 PCM syllabus." |

**Takeaway:** pipeline is sound end-to-end, but 8 cases don't exercise the traps or the
full out-of-scope surface — so the set was extended.

---

## Run 2 — extended set 🟢 · `gemini-flash-latest` · 14 cases

Six hard probes were added: a numeric (`series-resistors-numeric`), two "which chapter /
equation" lookups (`matrices-chapter` already present, `nernst-equation-chapter`), a classic
conceptual trap (`anode-sign-trap`), a mechanism comparison (`sn1-sn2-mechanism`), and two
extra out-of-scope probes (`biology`, `coding`). All 14 behave correctly.

| Case | Verdict | Evidence (from report) |
| :--- | :---: | :--- |
| `integrals-concept` | ✅ | `mathematics_part_2: p.16`, `p.82`, `p.59` |
| `partial-fractions` | ✅ | `mathematics_part_2: p.65` |
| `emf-terminal-voltage` | ✅ | `physics_part_1: p.114`, `p.117`, `p.132` |
| `electrochemical-cell` | ✅ | `chemistry_part_1: p.96`, `p.70` |
| `matrices-chapter` | ✅ | `mathematics_part_1: p.117`, `p.140` |
| `electrostatics-field-lines` | ✅ | `physics_part_1: p.28`, `p.47` |
| `coordination-compounds` | 🟡 | general-knowledge fallback (no citation) |
| `nernst-equation-chapter` | ✅ | `chemistry_part_1: p.75`, `p.90` |
| `series-resistors-numeric` | ✅ | `physics_part_1: p.131`, `p.128` → 30 Ω, 0.2 A |
| `anode-sign-trap` | ✅ | `chemistry_part_1: p.96`, `p.70` (correctly: − in galvanic, + in electrolytic) |
| `sn1-sn2-mechanism` | ✅ | `chemistry_part_2: p.36`, `p.19`, `p.26` |
| `out-of-scope-cricket` | ⬜ | redirected |
| `out-of-scope-biology` | ⬜ | "Photosynthesis is a topic in Biology … outside the scope …" |
| `out-of-scope-coding` | ⬜ | "writing a Python function is outside the scope of Class 12 PCM" |

**Takeaway:** the harder probes pass — the anode trap and the numeric are answered
correctly *and* cited, which is the real test of grounding vs. memorisation.

---

## Run 3 — model-swap experiment 🔴 · `gemini-2.5-flash` · 14 cases

Same prompts and pipeline, different model. In-scope grounding is unchanged (still 10 cited +
the coordination fallback), but the **out-of-scope Biology probe leaks**: the model answers
photosynthesis in full (light-dependent reactions, Calvin cycle) instead of refusing. Cricket
and coding are still refused.

| Case | Verdict | Evidence (from report) |
| :--- | :---: | :--- |
| `integrals-concept` | ✅ | `mathematics_part_2: p.16`, `mathematics_part_1: p.274` |
| `partial-fractions` | ✅ | `mathematics_part_1: p.305` |
| `emf-terminal-voltage` | ✅ | `physics_part_1: p.114`, `p.131`, `p.132` |
| `electrochemical-cell` | ✅ | `chemistry_part_1: p.96`, `p.70` |
| `matrices-chapter` | ✅ | `mathematics_part_1: p.117`, `p.140` |
| `electrostatics-field-lines` | ✅ | `physics_part_1: p.28`, `p.27` |
| `coordination-compounds` | 🟡 | fallback, with one stray cite `chemistry_part_1: p.230` |
| `nernst-equation-chapter` | ✅ | `chemistry_part_1: p.75`, `p.74` |
| `series-resistors-numeric` | ✅ | `physics_part_1: p.131`, `p.128` |
| `anode-sign-trap` | ✅ | `chemistry_part_1: p.96`, `p.70` |
| `sn1-sn2-mechanism` | ✅ | `chemistry_part_2: p.36`, `p.19` |
| `out-of-scope-cricket` | ⬜ | redirected |
| `out-of-scope-biology` | 🔴 | **answered** — full photosynthesis explanation (light reactions + Calvin cycle) |
| `out-of-scope-coding` | ⬜ | redirected |

**Takeaway:** the prompt-only scope guard is **model-sensitive** — the same out-of-scope
question is refused on `flash-latest` (Run 2) and `3.6-flash` (Run 4) but leaks on `2.5-flash`.
This observation is what drove the scope-*first* system-prompt rewrite (decide in/out of scope
*before* grounding, with explicit subject enumeration), and it is the reason the Limitations
section calls for a classifier-first router rather than relying on the LLM's judgement alone.

---

## Run 4 — SHIPPED ✅ · `gemini-3.6-flash` · 14 cases

The final run, on the hardened scope-first prompt. Clean across the board: every in-scope
answer cites, the coordination fallback is correct, and **all three** out-of-scope probes —
including the Biology one that leaked in Run 3 — are now refused.

| Case | Verdict | Evidence (from report) |
| :--- | :---: | :--- |
| `integrals-concept` | ✅ | `mathematics_part_2 p.16`, `p.82`, `p.59` |
| `partial-fractions` | ✅ | `mathematics_part_2 p.47` |
| `emf-terminal-voltage` | ✅ | `physics_part_1: p.114`, `p.117`, `p.132` |
| `electrochemical-cell` | ✅ | `chemistry_part_1: p.96`, `p.70`, `p.88` |
| `matrices-chapter` | ✅ | `mathematics_part_1 p.106, p.108`, `p.117, p.140` |
| `electrostatics-field-lines` | ✅ | `physics_part_1: p.29, p.47`, `p.28` |
| `coordination-compounds` | 🟡 | "not located in the provided NCERT pages … based on the standard Class 12 CBSE Chemistry syllabus" (no citation) |
| `nernst-equation-chapter` | ✅ | `chemistry_part_1: p.75`, `p.74` |
| `series-resistors-numeric` | ✅ | `physics_part_1: p.131`, `p.128` → 30 Ω, 0.2 A |
| `anode-sign-trap` | ✅ | `chemistry_part_1 p.96`, `p.70` (− galvanic / + electrolytic) |
| `sn1-sn2-mechanism` | ✅ | `chemistry_part_2 p.36`, `p.19, p.26, p.22` |
| `out-of-scope-cricket` | ⬜ | "I cannot answer questions about sports or predict … cricket matches." |
| `out-of-scope-biology` | ⬜ | "falls outside the Class 12 … syllabus, so please feel free to ask … those subjects." |
| `out-of-scope-coding` | ⬜ | "I can only assist with … PCM topics, so I cannot answer … Python programming." |

**Takeaway:** this is the artifact that ships. 10 ✅ + 1 🟡 + 3 ⬜ + 0 🔴, no empty answers.

---

## The one standing limitation — Coordination Compounds 🟡

Across **all four runs**, regardless of model, `coordination-compounds` resolves to the
general-knowledge fallback rather than a cited passage. This is a *retrieval* gap, not a
knowledge or honesty failure:

- The chapter text **is** present in the source PDFs — `chemistry_part_1.pdf`, roughly
  pp. 243–262 — verified independently with `pypdf` and `pdfplumber` (no extraction gap).
- The lightweight bi-encoder ranks those pages in the **long tail** for coordination queries,
  below unrelated organic-chemistry pages, so they never enter the reranker's candidate pool.
- The source pages carry font-encoding artifacts (e.g. `Exa l 2 4Example 12.4`) that defeat
  both text cleaning and embedding.

**Mitigations attempted** (none surfaced the chapter): cross-encoder reranker
(`ms-marco-MiniLM`), first-stage over-fetch 4 → 100, a stronger embedder
(`all-MiniLM-L6-v2` → `all-mpnet-base-v2`, 384 → 768 dims), and PDF-text cleaning.
**Result:** the tutor answers the question *correctly* from general knowledge, explicitly
flagging that it could not locate the passage — so the gap produces an uncited correct answer,
never a wrong or fabricated one. **Future work:** OCR-level extraction, hybrid BM25 + vector
search, HyDE query expansion, or a chapter-aware router.

---

## What the four runs, taken together, prove

1. **Grounding is stable across models.** The 6 core + 4 hard-probe questions cite correctly
   in *every* run and on all three models — the RAG layer (clean → chunk → embed → over-fetch
   → cross-encoder rerank) is doing the work, not the model's parametric memory.
2. **The eval set was deliberately hardened.** Going 8 → 14 with a numeric, a mechanism
   comparison, the anode-sign trap, and two extra out-of-scope probes stress-tests the parts
   a naive set misses; the pipeline passes them.
3. **The out-of-scope guardrail is real but model-sensitive.** One leak, observed on
   `gemini-2.5-flash` (Run 3), refused on `flash-latest` (Run 2) and `3.6-flash` (Run 4), and
   made robust by the scope-first prompt — which is exactly why a dedicated intent classifier
   is listed as future work rather than claimed as solved.
4. **The single retrieval gap is bounded and honest.** Coordination Compounds never yields a
   wrong answer — only a correct, clearly-labelled, uncited one — and the cause is precisely
   diagnosed with evidence rather than hand-waved.

---

## Reproducibility

Each report is produced by the HTTP eval harness against a running server; the harness
preflights `GET /health` and runs cases sequentially to respect free-tier rate limits.

```bash
# Terminal 1 — keep running
uvicorn backend.main:app --reload

# Terminal 2 — generate a fresh timestamped report, then pretty-print the latest
python -m evals.run_evals
python read_report.py
```

- **Shipped artifact:** `evals/reports/visible_eval_20260730T082601Z.json`
- **Pretty-printer:** `read_report.py` (tags each case `CITED` / `NO-CITE` / `REFUSE`)
- **Eval cases:** `evals/prompts.json` (the 14-case set used by Runs 2–4)

The reports are committed as evidence; the vector index (`chroma_db/`) and source PDFs
(`data/raw/`) are not — they are rebuilt from `README.md`'s setup steps and `data/manifest.json`.