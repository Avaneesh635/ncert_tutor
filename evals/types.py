from pydantic import BaseModel


class EvalCase(BaseModel):
    id: str
    prompt: str


class EvalResult(BaseModel):
    id: str
    answer: str
    model: str
