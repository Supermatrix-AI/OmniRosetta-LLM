from schemas.io_schema import AgentOutput


def format_output(answer: str, confidence: float) -> dict:
    out = AgentOutput(answer=answer, confidence=confidence)
    print(out.json(indent=2))
    return out.dict()
