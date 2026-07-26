#3rd agent
from langchain_google_genai import ChatGoogleGenerativeAI #Imports the Gemini AI model wrapper from LangChain. This lets you talk to Gemini using LangChain's standard interface instead of raw API calls.
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage #a special wrapper that tells Claude "this message is coming from a human/user." gemini expects messages to be labeled by who sent them (Human, AI, System).
from graph.state import AgentState #Google Doc that all agents can read and write to
from utils.search import search_web  #Tavily ke responses in list forms  import funciton name search_web

# chromaDB stuff
from utils.chroma_store import save_research, load_research

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=5)
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)   # Instantiates gemini at module level  | reliable routing decisions, not creative ones.  therefore temp is zero

def benchmarking_node(state: AgentState) -> AgentState:
    query = state["query"]

    #check if that query is in cahce or not
    cached = load_research(query, "benchmarking")
    if cached:
        print("✓ Benchmarking: loaded from cache")
        return {
            "benchmarking_output": cached,
            "completed_agents": ["benchmarking"],
        }

    raw = search_web(f"{query} competitors comparison market share benchmark industry peers")

    prompt = f"""You are a benchmarking specialist at McKinsey.
Identify 3-4 key competitors of the company/sector in "{query}".
For each, note their key strengths vs the subject company.
Format as a brief comparison table (text form is fine).

Search results:
{raw}"""

    response = llm.invoke([HumanMessage(content=prompt)])

    # Save to cache
    save_research(query, "benchmarking", response.content)

    return {
        "benchmarking_output": response.content,
        "completed_agents": ["benchmarking"],
    }