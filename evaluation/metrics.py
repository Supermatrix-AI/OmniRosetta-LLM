import datetime
import json


def log_eval(query, result, score):
    log = {
        "ts": datetime.datetime.now().isoformat(),
        "query": query,
        "score": score,
    }
    with open("evaluation/logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")
