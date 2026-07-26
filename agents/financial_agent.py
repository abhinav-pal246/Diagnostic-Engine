# 2nd agent 
from langchain_google_genai import ChatGoogleGenerativeAI #Imports the Gemini AI model wrapper from LangChain. This lets you talk to Gemini using LangChain's standard interface instead of raw API calls.
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage #a special wrapper that tells Claude "this message is coming from a human/user." gemini expects messages to be labeled by who sent them (Human, AI, System).
from graph.state import AgentState #Google Doc that all agents can read and write to
from utils.search import search_web  #Tavily ke responses in list forms  import funciton name search_web

# chromaDB stuff
from utils.chroma_store import save_research, load_research

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=5)
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)   # Instantiates gemini at module level  | reliable routing decisions, not creative ones.  therefore temp is zero


def financial_node(state: AgentState) -> AgentState:
    query = state["query"]

    #check if that query is in cahce or not
    cached = load_research(query, "financial")
    if cached:
        print("✓ Financial: loaded from cache")
        return {
            "financial_output": cached,
            "completed_agents": ["financial"],
        }
    raw = search_web(f"{query} revenue profit margin EBITDA financial results 2024")

    prompt = f"""You are a financial analyst at McKinsey.
From these results about "{query}", extract a financial health snapshot.
Cover: revenue trend, profitability, key ratios if available.
Format as a short structured summary (3-5 points).

Search results:
{raw}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Save to cache
    save_research(query, "financial", response.content)

    return {
        "financial_output": response.content,
        "completed_agents": ["financial"],
    }