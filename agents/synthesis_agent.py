#It's the "brain" node of your multi-agent consulting tool — it takes all the research gathered by 4 
# parallel agents and asks Claude to synthesize it into a structured McKinsey-style diagnostic report.


#5th agent
from langchain_google_genai import ChatGoogleGenerativeAI #Imports the Gemini AI model wrapper from LangChain. This lets you talk to Gemini using LangChain's standard interface instead of raw API calls.
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage #a special wrapper that tells Claude "this message is coming from a human/user." gemini expects messages to be labeled by who sent them (Human, AI, System).
from graph.state import AgentState #Google Doc that all agents can read and write to
from utils.search import search_web  #Tavily ke responses in list forms  import funciton name search_web


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=5)
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)   # Instantiates gemini at module level  | reliable routing decisions, not creative ones.  therefore temp is zero

def synthesis_node(state: AgentState) -> AgentState:
    prompt = f"""You are a senior McKinsey consultant writing an executive diagnostic.
Structure your output using the Situation → Complication → Resolution framework.

Query: {state['query']}

Research Brief:
{state.get('research_output', 'N/A')} 

Financial Snapshot:
{state.get('financial_output', 'N/A')}

Competitive Benchmark:
{state.get('benchmarking_output', 'N/A')}

Industry Trends:
{state.get('trends_output', 'N/A')}

---
Write a McKinsey-style rapid diagnostic with:
1. **Situation** – What is true today (2-3 sentences)
2. **Complication** – The core tension or challenge (2-3 sentences)  
3. **Resolution** – 3-5 recommended actions with rationale
4. **Key Risks** – 2 risks to watch

Be direct, specific, and use data where available."""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        "synthesis_output": response.content,
        "completed_agents": ["synthesis"],
    }
    













#Python dictionary method used to retrieve data safely Here is the breakdown of what state.get('research_output', 'N/A') actually does:

# 1. The Breakdown
# state: The dictionary object holding your agent's data.

# .get(): A built-in Python method that looks for a specific key.

# 'research_output': The specific key (piece of information) you are looking for.

# 'N/A': The fallback/default value. If the key doesn't exist, return this instead of crashing.