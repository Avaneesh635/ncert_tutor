"""One-time indexer. Run from the project root:  python -m backend.ingest"""
from backend import rag

if __name__ == "__main__":
    n = rag.ingest()
    if n == 0:
        print("No PDFs in data/raw/ yet. Add the 6 NCERT books, then re-run this command.")
    else:
        print(f"Indexed {n} chunks into chroma_db/. The tutor will now cite the books.")