from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.agent import StarterAgent
from backend.types import ChatRequest, ChatResponse

load_dotenv(Path(__file__).with_name(".env"))

app = FastAPI(title="NCERT Tutor Assignment")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = StarterAgent()

FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


@app.get("/")
def index() -> FileResponse:
    """Serve the chat UI (same origin -> no CORS juggling)."""
    return FileResponse(FRONTEND)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return agent.answer(request)