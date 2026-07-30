"""Retrieval layer: clean + chunk the NCERT PDFs into a searchable vector index,
then re-rank the top candidates with a cross-encoder for precision."""
from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass
from typing import Any

import chromadb
from sentence_transformers import CrossEncoder, SentenceTransformer

from backend.constants import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBED_MODEL,
    RAW_PDF_DIR,
    TOP_K,
)

# --- reranker settings (query-time only; no re-ingest needed) ---
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"   # free, local
RETRIEVE_OVER_FETCH = 100                                # wide net, then cut to TOP_K

_embedding_model: SentenceTransformer | None = None
_reranker: CrossEncoder | None = None
_collection: Any = None


def clean(text: str) -> str:
    """Strip PDF extraction junk so embeddings reflect real content, not headers."""
    if not text:
        return ""
    text = re.sub(r"C:\\[^\n]*\.pmd[^\n]*", "", text)   # drop "C:\...\Unit-X.pmd ..." header lines
    text = re.sub(r"-\n", "", text)                     # de-hyphenate wrapped words
    text = re.sub(r"(?<=\S)\n(?=\S)", " ", text)        # merge broken line wraps
    text = re.sub(r"[ \t]+", " ", text)                 # collapse horizontal whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)              # collapse blank lines
    return text.strip()


@dataclass(frozen=True)
class Passage:
    text: str
    book: str
    page: int


def _model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBED_MODEL)
    return _embedding_model


def _rerank_model() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANK_MODEL)
    return _reranker


def _get_collection() -> Any:
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_or_create_collection(name="ncert")
    return _collection


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if not text:
        return []
    step = max(1, size - overlap)
    return [text[i : i + size] for i in range(0, len(text), step)]


def ingest() -> int:
    """Read every PDF in data/raw/, clean+chunk+embed, store in Chroma. Returns chunk count."""
    from pypdf import PdfReader  # lazy import

    collection = _get_collection()
    if collection.count() > 0:
        return int(collection.count())  # already built -> idempotent

    pdf_paths = sorted(glob.glob(os.path.join(RAW_PDF_DIR, "*.pdf")))
    if not pdf_paths:
        return 0

    model = _model()
    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict[str, str | int]] = []
    n = 0
    for path in pdf_paths:
        book = os.path.basename(path)
        reader = PdfReader(path)
        for page_num, page in enumerate(reader.pages, start=1):
            for chunk in chunk_text(clean(page.extract_text() or "")):
                if len(chunk.strip()) < 40:   # skip empty / garbage chunks
                    continue
                ids.append(f"{book}:p{page_num}:c{n}")
                docs.append(chunk)
                metas.append({"book": book, "page": page_num})
                n += 1

    for start in range(0, len(docs), 64):
        embs = model.encode(docs[start : start + 64]).tolist()
        collection.add(
            ids=ids[start : start + 64],
            documents=docs[start : start + 64],
            metadatas=metas[start : start + 64],
            embeddings=embs,
        )
    return n


def retrieve(question: str, k: int = TOP_K) -> list[Passage]:
    """Over-fetch with the bi-encoder, re-rank with a cross-encoder, return top k."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    embedding = _model().encode([question]).tolist()
    n = min(RETRIEVE_OVER_FETCH, int(collection.count()))
    res = collection.query(query_embeddings=embedding, n_results=n)

    docs = res["documents"]
    metas = res["metadatas"]
    if not docs or not metas or not docs[0] or not metas[0]:
        return []
    candidates = [(str(t), m) for t, m in zip(docs[0], metas[0]) if t and m]
    if not candidates:
        return []

    if len(candidates) > k:
        scores = _rerank_model().predict([[question, t] for t, _ in candidates])
        order = sorted(range(len(scores)), key=lambda i: float(scores[i]), reverse=True)[:k]
        candidates = [candidates[i] for i in order]
    else:
        candidates = candidates[:k]

    return [
        Passage(text=t, book=str(m.get("book", "")), page=int(m.get("page", 0)))
        for t, m in candidates
    ]