from fastapi import FastAPI
from guardrail import run_with_guardrail
import csv
import os
from datetime import datetime

def log_run(total, accuracy, confidently_wrong_count):
    file_exists = os.path.exists("guardrail_log.csv")
    with open("guardrail_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "total", "accuracy", "confidently_wrong_count", "status"])
        status = "alert" if confidently_wrong_count > 0 else "healthy"
        writer.writerow([datetime.now().isoformat(), total, accuracy, confidently_wrong_count, status])

app_api = FastAPI()

@app_api.get("/run-guardrail")
def run_guardrail_endpoint():
    results = run_with_guardrail()
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    confidently_wrong = [r for r in results if r["flag"] == "🚨 CONFIDENTLY WRONG"]

    log_run(total, round(correct / total * 100, 1), len(confidently_wrong)) 
 
    return {
        "total": total,
        "accuracy": round(correct / total * 100, 1),
        "confidently_wrong_count": len(confidently_wrong),
        "confidently_wrong_cases": confidently_wrong
    }