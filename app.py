from fastapi import FastAPI

from src.core.multi_agent import orchestrate

app = FastAPI(title="OmniRosetta-LLM API")


@app.get("/ask")
def ask(q: str):
    return {"response": orchestrate(q)}
