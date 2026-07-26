# Supervisor Node — the brain/manager of  multi-agent system. Its job is simple: read the user's 
# query and decide which agents need to run. It's like a consulting project manager who receives a 
# client brief and assigns tasks to the right team members.

from langchain_google_genai import ChatGoogleGenerativeAI #Imports the Gemini AI model wrapper from LangChain. This lets you talk to Gemini using LangChain's standard interface instead of raw API calls.
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage #a special wrapper that tells Claude "this message is coming from a human/user." gemini expects messages to be labeled by who sent them (Human, AI, System).
from graph.state import AgentState #Google Doc that all agents can read and write to

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_retries=5)
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0) # Instantiates gemini at module level  | reliable routing decisions, not creative ones.  therefore temp is zero

#instruction manual you give Gemini.
SUPERVISOR_PROMPT = """You are a McKinsey-style research supervisor.
Given a business query, decide which research tracks to run.
Always return a JSON with key "next_agents" listing agents to run.
Available agents: research, financial, benchmarking, trends
Example: {{"next_agents": ["research", "financial", "benchmarking", "trends"]}}
Query: {query}"""

def supervisor_node(state: AgentState) -> AgentState: #take agentstate as input and return agentstate updated memory
    import json

    prompt = SUPERVISOR_PROMPT.format(query = state["query"]) #supervisor_prompt ki query dynamically change 

    response = llm.invoke([HumanMessage(content=prompt)]) #LLMs expect a "conversation history." Even if it's just one message, || it must be inside a list. HumanMessage: This is a class from langchain_core.messages
    #llm.invoke is the "Send" button , ai start fetching the response

    try:
        parsed = json.loads(response.content) #response.content  -> the actual text gemini wrote , gemini will respnd in this format ex-> '{"next_agents": ["research", "financial"]}' as we specifi in supervisor_promt
        agents = parsed.get("next_agents", ["research", "financial", "benchmarking", "trends"]) #.get() is a safe way to extract a value from a dictionary. 
        # dictionary.get("key", "fallback value")                         
                     #what to find    what to return IF not found.  || if next_agents doesn't exist — give me all 4 agents as default."
    except Exception:
        agents = ["research", "financial", "benchmarking", "trends"]

    return {
    "messages": [response],
    }

    









# import json theory
#  BEFORE json.loads() — just text, can't use it
# response.content = '{"next_agents": ["research", "financial"]}'

# # AFTER json.loads() — real Python dictionary!
# parsed = json.loads(response.content)
# # → {"next_agents": ["research", "financial"]}


#HumanMEssage theory
# This is how it 'lives' inside the []
# messages = [
#     SystemMessage(content=SUPERVISOR_PROMPT.format(query="Should we invest in EV charging?")),
#     HumanMessage(content="Please start the analysis.")
# ]