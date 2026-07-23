#1st doing research agent
from langchain_google_genai import ChatGoogleGenerativeAI #Imports the Gemini AI model wrapper from LangChain. This lets you talk to Gemini using LangChain's standard interface instead of raw API calls.
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage #a special wrapper that tells Claude "this message is coming from a human/user." gemini expects messages to be labeled by who sent them (Human, AI, System).
from graph.state import AgentState #Google Doc that all agents can read and write to
from utils.search import search_web  #Tavily ke responses in list forms  import funciton name search_web

# chromaDB stuff
from utils.chroma_store import save_research, load_research


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)   # Instantiates gemini at module level  | reliable routing decisions, not creative ones.  therefore temp is zero


#hi
def research_node(state: AgentState) -> AgentState:
    query = state["query"]

    

    #check if that query is in cahce or not
    cached = load_research(query, "research")
    if cached:
        print("✓ Research: loaded from cache")
        return {
            "research_output": cached,
            "completed_agents": ["research"],
        }



    raw = search_web(f"{query} latest news strategy operations 2024 2025") # asking tavily to return the data in desired format

    prompt = f"""You are a McKinsey research analyst. 
    Synthesize these search results about "{query}" into a concise research brief.
    Focus on: recent developments, strategic moves, major challenges.
    Keep it to 3-4 bullet points max.
    Search results:
    {raw}"""

    response = llm.invoke([HumanMessage(content=prompt)])

    # Save to cache
    save_research(query, "research", response.content)
    
    return {
        "research_output": response.content,
        "completed_agents": ["research"], #add
    }
    



#Tavily is returning responses in this format 
# {
#      "title": "Tata Steel Reports Q4 2024 Results",
#     "url": "https://tatasteel.com/investors/q4-2024",
#      "content": "Tata Steel reported a revenue of $21 billion...",
#      "score": 0.95
#  }