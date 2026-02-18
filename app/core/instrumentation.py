import time
import json
from pathlib import Path

LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def instrument_run(run_func, question: str) -> dict:
    start = time.time()
    result = run_func(question)
    latency = time.time() - start

    result["latency"] = latency

    # Persist structured log
    log_payload = {
        "question": question,
        "mode": run_func.__name__,
        "metrics": {
            "coverage": result.get("coverage"),
            "tokens": result.get("tokens"),
            "latency": latency
        }
    }

    log_file = LOG_DIR / f"log_{int(time.time())}.json"

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_payload, f, indent=2)

    return result
