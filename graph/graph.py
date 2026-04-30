from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import AgentState
from graph.supervisor import supervisor_node
from agents.research_agent import research_node
from agents.financial_agent import financial_node
from agents.benchmarking_agent import benchmarking_node
from agents.trends_agent import trends_node
from agents.synthesis_agent import synthesis_node

def human_review_node(state: AgentState) -> AgentState:
    """Pause point — Streamlit will handle the actual review UI."""
    return state

def build_graph():
    g = StateGraph(AgentState)

    g.add_node("supervisor", supervisor_node)
    g.add_node("research", research_node)
    g.add_node("financial", financial_node)
    g.add_node("benchmarking", benchmarking_node)
    g.add_node("trends", trends_node)
    g.add_node("human_review", human_review_node)
    g.add_node("synthesis", synthesis_node)

    g.set_entry_point("supervisor")

    g.add_edge("supervisor", "research")
    g.add_edge("supervisor", "financial")
    g.add_edge("supervisor", "benchmarking")
    g.add_edge("supervisor", "trends")

    # All agents → human review → synthesis
    g.add_edge("research", "human_review")
    g.add_edge("financial", "human_review")
    g.add_edge("benchmarking", "human_review")
    g.add_edge("trends", "human_review")

    g.add_edge("human_review", "synthesis")
    g.add_edge("synthesis", END)

    # ← this enables HITL interruption
    checkpointer = MemorySaver()
    return g.compile(
        checkpointer=checkpointer,
        interrupt_before=["synthesis"]
    )

diagnostic_graph = build_graph()