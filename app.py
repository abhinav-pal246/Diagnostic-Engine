from dotenv import load_dotenv
load_dotenv()

from graph.graph import diagnostic_graph
from langchain_core.messages import HumanMessage

def run_diagnostic(query: str):
    initial_state = {
        "query": query,
        "research_output": "",
        "financial_output": "",
        "benchmarking_output": "",
        "trends_output": "",
        "synthesis_output": "",
        "messages": [HumanMessage(content=query)],
        "completed_agents": [],
    }
    result = diagnostic_graph.invoke(initial_state)
    return result["synthesis_output"]

if __name__ == "__main__":
    output = run_diagnostic("Analyze Tata Steel's operational efficiency")
    print("=== DIAGNOSTIC REPORT ===")
    print(output)