import os
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate
from eval_dataset import eval_data
from agent import app

load_dotenv()

client = Client()

DATASET_NAME = "ticket-classifier-eval"

# Create the dataset in LangSmith (only needs to run once)
def setup_dataset():
    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        print("Dataset already exists, skipping creation.")
        return existing[0]

    dataset = client.create_dataset(dataset_name=DATASET_NAME)
    for item in eval_data:
        client.create_example(
            inputs={"ticket_text": item["ticket_text"]},
            outputs={"expected": item["expected"]},
            dataset_id=dataset.id
        )
    print(f"Created dataset with {len(eval_data)} examples.")
    return dataset

# Wraps your LangGraph agent so LangSmith can call it per example
def target(inputs: dict) -> dict:
    result = app.invoke({
        "ticket_text": inputs["ticket_text"],
        "category": "",
        "confidence": "",
        "reasoning": ""
    })
    return {"category": result["category"], "confidence": result["confidence"]}

# Custom evaluator: did the predicted category match the expected one?
def correctness_evaluator(run, example) -> dict:
    predicted = run.outputs.get("category", "").strip().lower()
    expected = example.outputs.get("expected", "").strip().lower()
    score = 1 if predicted == expected else 0
    return {"key": "correctness", "score": score}

if __name__ == "__main__":
    setup_dataset()

    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator],
        experiment_prefix="ticket-classifier-v1"
    )

    print("Evaluation complete. Check the LangSmith dashboard for results.")