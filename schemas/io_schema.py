from pydantic import BaseModel


class AgentInput(BaseModel):
    query: str
    context: dict | None = None


class AgentOutput(BaseModel):
    answer: str
    confidence: float
