import os
from typing import cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from backend import rag
from backend.constants import SYSTEM_PROMPT
from backend.types import ChatRequest, ChatResponse

# Used ONLY if the model returns an empty completion (e.g., a safety-filtered
# prediction query). Guarantees the tutor never answers with a blank.
FALLBACK_PROMPT = (
    "You are a CBSE Class 12 Physics, Chemistry, and Mathematics tutor. "
    "Answer the student's question from your own knowledge, clearly and at a Class 12 level. "
    "If the question is outside Class 12 PCM, politely decline and redirect to the PCM syllabus."
)
DEFAULT_REFUSAL = (
    "I'm a tutor for CBSE Class 12 Physics, Chemistry, and Mathematics. "
    "Please ask me a question within that syllabus and I'll be glad to help!"
)


class StarterAgent:
    """NCERT Class 12 tutor: Gemini grounded in the NCERT PDFs via retrieval."""

    def __init__(self) -> None:
        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/",
            api_key=os.environ["GEMINI_API_KEY"],
            max_retries=5,
            timeout=120.0,
        )
        self.model = "gemini-3.6-flash"  # proven to answer coordination + refuse cricket

    def _generate(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=cast(list[ChatCompletionMessageParam], messages),
        )
        return (response.choices[0].message.content or "").strip()

    def answer(self, request: ChatRequest) -> ChatResponse:
        if not request.messages:
            return ChatResponse(answer=DEFAULT_REFUSAL, model=self.model)

        question = request.messages[-1].content

        # 1. Retrieve the most relevant textbook passages (empty until ingested).
        passages = rag.retrieve(question)
        if passages:
            context = "\n\n".join(
                f"[Source: {p.book.replace('.pdf', '')} p.{p.page}]\n{p.text}"
                for p in passages
            )
            user_content = f"Textbook context:\n{context}\n\nStudent question: {question}"
        else:
            user_content = question  # no relevant context -> model answers from knowledge

        # 2. System prompt + prior turns + grounded current question.
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in request.messages[:-1]:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_content})

        # 3. Generate; if the model returns empty, retry once in general-knowledge mode.
        content = self._generate(messages)
        if not content:
            content = self._generate(
                [{"role": "system", "content": FALLBACK_PROMPT},
                 {"role": "user", "content": question}]
            )
        if not content:
            content = DEFAULT_REFUSAL  # last resort: never return a blank

        return ChatResponse(answer=content, model=self.model)