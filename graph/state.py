# from typing import TypedDict, List, Annotated
# from langchain_core.messages import BaseMessage
# import operator


# class AgentState(TypedDict):
#     query: str
#     research_output: str
#     financial_output: str
#     benchmarking_output: str
#     trends_output: str
#     synthesis_output: str
#     messages: Annotated[List[BaseMessage], operator.add]  #it holds chat messages and operator.add append the message
#     completed_agents: List[str]
#     next_agents: List[str] 


from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
import operator

def take_last(a, b):
    return b

class AgentState(TypedDict):
    query: Annotated[str, take_last]
    research_output: Annotated[str, take_last]
    financial_output: Annotated[str, take_last]
    benchmarking_output: Annotated[str, take_last]
    trends_output: Annotated[str, take_last]
    synthesis_output: Annotated[str, take_last]
    messages: Annotated[List[BaseMessage], operator.add]
    completed_agents: Annotated[List[str], operator.add]


#     so when 4 agents tried to write query simultaneously LangGraph didn't know which value to keep.
# take_last just says "if multiple agents write to this field, keep the last one"
#  — which is the correct behavior for string output fields.
