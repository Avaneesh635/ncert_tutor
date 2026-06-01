from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from backend.agent import StarterAgent
from backend.types import ChatRequest, ChatResponse


load_dotenv(Path(__file__).with_name(".env"))

app = FastAPI(title="NCERT Tutor Assignment")
agent = StarterAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    return agent.answer(request)
