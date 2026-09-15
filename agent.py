import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langfuse import observe
from typing import TypedDict

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

class AgentState(TypedDict):
    ticket_text: str
    category: str
    confidence: str
    reasoning: str

@observe(name="classify_ticket")
def classify_node(state: AgentState) -> AgentState:
    prompt = f"""Classify this support ticket into exactly one category:
Billing, Technical, General, or Account.

Ticket: "{state['ticket_text']}"

Respond in this exact format:
Category: <category>
Confidence: <High/Medium/Low>
Reasoning: <one short sentence>
"""
    response = llm.invoke(prompt).content

    lines = response.strip().split("\n")
    state["category"] = lines[0].replace("Category:", "").strip()
    state["confidence"] = lines[1].replace("Confidence:", "").strip()
    state["reasoning"] = lines[2].replace("Reasoning:", "").strip()
    return state

graph = StateGraph(AgentState)
graph.add_node("classify", classify_node)
graph.set_entry_point("classify")
graph.add_edge("classify", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({
        "ticket_text": "I was charged twice for my subscription this month",
        "category": "",
        "confidence": "",
        "reasoning": ""
    })
    print(result)