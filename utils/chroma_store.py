# First run:   Query → Tavily → Groq → Save to ChromaDB → Show result
# Second run:  Query → ChromaDB hit → Show result  (Tavily + Groq skipped)

#it prevents re-fetching the same data if you re-run the pipeline, which saves Tavily API costs 
# and speeds up iteration during development.

# ChromaDB stores data as embeddings—which are essentially lists of numbers that represent the meaning of information.
#unlike row and column
#Vector Storage: It converts text, images, or audio into "vectors" (mathematical coordinates).

import os
import shutil
import chromadb #vector database library for storing and retrieving text
import hashlib #built-in Python library for generating hash values (like fingerprints for strings)
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
# ↑ FIX: ChromaDB's default embedding function (ONNXMiniLM_L6_V2) uses onnxruntime,
# which is broken on Python 3.14 (the version Streamlit Cloud uses).
# SentenceTransformerEmbeddingFunction uses the same underlying model (all-MiniLM-L6-v2)
# but loads it via the sentence-transformers library instead — no ONNX, no crash.
# Add "sentence-transformers" to requirements.txt for this to work.

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# Downloads ~80MB on first run. Cached after that. Same model, same vector quality.

CHROMA_PATH = "./chroma_db"

# The persisted collection may have been created with a different embedding
# function (e.g. the default ONNX one), which is incompatible with the
# SentenceTransformer function we use here — and on Python 3.14 the old ONNX
# module can fail even to load, so `delete_collection` can raise too.
# Fallback: nuke the on-disk store entirely and start clean. Cached vectors
# from a different embedding model would be meaningless anyway.
def _open_collection():
    global client
    try:
        return client.get_or_create_collection(
            "research_cache",
            embedding_function=embedding_fn,
        )
    except Exception:
        try:
            client.delete_collection("research_cache")
            return client.get_or_create_collection(
                "research_cache",
                embedding_function=embedding_fn,
            )
        except Exception:
            if os.path.exists(CHROMA_PATH):
                shutil.rmtree(CHROMA_PATH, ignore_errors=True)
            client = chromadb.PersistentClient(path=CHROMA_PATH)
            return client.get_or_create_collection(
                "research_cache",
                embedding_function=embedding_fn,
            )

client = chromadb.PersistentClient(path=CHROMA_PATH) #Creates a ChromaDB client that saves data to disk at the folder ./chroma_db. "Persistent" means data survives after your program closes (unlike in-memory storage).
collection = _open_collection() #this one stores all your cached research.

def get_cache_key(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest() #md5 requires bytes  query.lower().strip().encode() is method chaining 

# .lower() — normalizes case ("Tata Steel" → "tata steel")
# .strip() — removes leading/trailing whitespace
# .encode() — converts string to bytes (MD5 requires bytes)
# hashlib.md5(...).hexdigest() — produces a 32-character hex string like "a3f2b1c9..."

def save_research(query: str, agent: str, content: str):
    key = f"{get_cache_key(query)}_{agent}" #Builds a unique ID combining the query hash + agent name. Example: "a3f2b1c9..._financial_agent"

    collection.upsert( #update if exists, insert if not. Stores:
        documents=[content],#he actual research text content
        ids=[key],
        metadatas=[{"query": query, "agent": agent}] #extra info tagged alongside (original query + which agent produced it)
    )

def load_research(query: str, agent: str) -> str | None:
    key = f"{get_cache_key(query)}_{agent}"
    try:
        result = collection.get(ids=[key])
        if result["documents"]:
            return result["documents"][0]
    except:
        pass
    return None #if not found data , agent will handle to call travily to search for

def clear_research(query: str):
    # Deletes cached entries for a specific query across all agents.
    # Call this before a HITL re-run so agents fetch fresh data instead of hitting stale cache.
    for agent in ("research_agent", "financial_agent", "benchmarking_agent", "trends_agent"):
        key = f"{get_cache_key(query)}_{agent}"
        try:
            collection.delete(ids=[key])
        except:
            pass


















# Turning Words into Coordinates
# Computers don't actually "understand" what a dog is. To a computer, a dog is just a string of characters: D-O-G.
# To bridge this gap, we use an AI model (an "Encoder") to turn that word into a long list of numbers—a vector.
# Dog: [0.12, -0.59, 0.88]
# Puppy: [0.11, -0.60, 0.85]
# Toaster: [0.99, 0.44, -0.21]

# When you ask ChromaDB a question, it doesn't look for the exact letters you typed. Instead:
# It turns your question into a vector (a coordinate).
# It looks at its "map" of stored data.
# It finds the data points that are mathematically closest to your coordinate.



## The Real World Flow
# Agent runs for the first time
#         ↓
# load_research("Tata Steel", "financial_agent")
#         ↓
# Returns None ← nothing saved yet
#         ↓
# Agent calls Tavily API → gets fresh data
#         ↓
# save_research("Tata Steel", "financial_agent", data)
#         ↓
# Data stored in ChromaDB 

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Agent runs AGAIN (second time)
#         ↓
# load_research("Tata Steel", "financial_agent")
#         ↓
# Returns cached text ← found it!
#         ↓
# Skip Tavily API call entirely 

# Why This Pattern Matters
# Without CacheWith CacheEvery run calls Tavily APIAPI called only onceCosts money every timeSaves API creditsSlow (network calls)Fast (local disk read)Same data fetched repeatedlyFetched once, reused

# Super Simple Summary

# save_research = "Remember this for later"
# load_research = "Do you remember this?"

# Together they make sure your agents never do the same work twice. That's called caching — one of the most important patterns in building efficient AI systems.



# Tavily returns:
# "Tata Steel reported a 12% revenue increase 
#  in Q3, driven by strong demand in Europe..."
#             │
#             ▼
#     collection.upsert(documents=[that text])
#             │
#             ▼
#     ChromaDB takes over...

# Step by Step — How ChromaDB Converts to Vector
# Step 1 — Text Gets Broken into Tokens
# "Tata Steel reported a 12% revenue increase"
#             ↓
# ["Tata", "Steel", "reported", "a", "12%", "revenue", "increase"]
# Words/subwords are split into tokens (small pieces)

# Step 2 — Each Token Gets a Number
# "Tata"     → 15420
# "Steel"    → 8731
# "reported" → 2341
# "revenue"  → 5621
# "increase" → 4392
# Every word in the English language has a pre-assigned number in the model's vocabulary