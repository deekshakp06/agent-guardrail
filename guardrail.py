import os
from dotenv import load_dotenv
from langsmith import Client
from langfuse import Langfuse, observe
from eval_dataset import eval_data
from agent import app

load_dotenv()

client = Client()
langfuse_client = Langfuse()

@observe(name="process_ticket")
def process_ticket(item):
    result = app.invoke({
        "ticket_text": item["ticket_text"],
        "category": "",
        "confidence": "",
        "reasoning": ""
    })

    predicted = result["category"].strip().lower()
    expected = item["expected"].strip().lower()
    confidence = result["confidence"].strip().lower()
    is_correct = predicted == expected

    # The key guardrail check: flag dangerous mismatches
    flag = None
    if confidence == "high" and not is_correct:
        flag = "🚨 CONFIDENTLY WRONG"
    elif confidence == "low" and is_correct:
        flag = "⚠️ UNDERCONFIDENT (correct but flagged as low)"

    # Log scores back to Langfuse while still inside this trace's context
    langfuse_client.score_current_trace(
        name="correctness",
        value=1 if is_correct else 0
    )
    if flag == "🚨 CONFIDENTLY WRONG":
        langfuse_client.score_current_trace(
            name="confident_wrong",
            value=1
        )

    return {
        "ticket": item["ticket_text"],
        "predicted": result["category"],
        "expected": item["expected"],
        "confidence": result["confidence"],
        "correct": is_correct,
        "flag": flag
    }

def run_with_guardrail():
    results = []
    for item in eval_data:
        results.append(process_ticket(item))
    return results

def print_report(results):
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    confidently_wrong = [r for r in results if r["flag"] == "🚨 CONFIDENTLY WRONG"]

    print(f"\n=== GUARDRAIL REPORT ===")
    print(f"Overall accuracy: {correct}/{total} ({correct/total*100:.0f}%)")
    print(f"Confidently wrong cases: {len(confidently_wrong)}")
    print()

    for r in results:
        status = "✅" if r["correct"] else "❌"
        print(f"{status} [{r['confidence']}] \"{r['ticket'][:50]}...\"")
        print(f"    Predicted: {r['predicted']} | Expected: {r['expected']}")
        if r["flag"]:
            print(f"    {r['flag']}")
        print()

if __name__ == "__main__":
    results = run_with_guardrail()
    print_report(results)
    langfuse_client.flush()  # ensure all scores are sent before the script exits