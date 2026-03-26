#routes 
#using Tavily api here

# This code defines a helper function that uses the Tavily API to perform deep web searches and retrieve summarized content based on a query.
#  It then cleans and formats those results into a single,
# vv imp 
#  structured string designed for an LLM agent to read and analyze.


import os #need this to read environment variables (like API keys)
from tavily import TavilyClient #This is the library that lets you talk to Tavily's search API without manually writing HTTP requests.

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))  #messanger between code and API services


#used type hint to tell use datatype focused variables
def search_web(query:str , max_results : int = 5) -> str :
    #Run a Tavily search and return a formatted string of results


    response = client.search(
        query=query,
        search_depth = "advanced",  #The key setting here is search_depth="advanced"  this tells Tavily to crawl and summarize the actual page content, not just return titles and URLS
        max_results=max_results,
    )
    results = response.get("results" , [])     #[] is holdind a results from Tavily 
    if not results:
        return "No results found."
    
    formatted = [] 
    #formatting the results in human readable form 
    for r in results:
        formatted.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSummary: {r['content']}\n"
        )
    return "\n---\n".join(formatted) #Joins all the individual result blocks into **one big string**, separated by `---` dividers. This single string is what gets passed to your LLM agent, which reads it like a briefing document and extracts insights from it.
    

# in an instance r= 
# r = {
#     "title": "Tata Steel Reports Q4 2024 Results",
#     "url": "https://tatasteel.com/investors/q4-2024",
#     "content": "Tata Steel reported a revenue of $21 billion...",
#     "score": 0.95
# }

# [
#     {"title": "...", "url": "...", "content": "...", "score": 0.95, ...},
#     {"title": "...", "url": "...", "content": "...", "score": 0.87, ...},
#     {"title": "...", "url": "...", "content": "...", "score": 0.76, ...},
#     {"title": "...", "url": "...", "content": "...", "score": 0.71, ...},
#     {"title": "...", "url": "...", "content": "...", "score": 0.65, ...},
# ]