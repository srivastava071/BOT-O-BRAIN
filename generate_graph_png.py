import urllib.request
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    memories: List[str]

def retrieve_node(state: State):
    return {}

def chat_node(state: State):
    return {}

def save_node(state: State):
    return {}

builder = StateGraph(State)
builder.add_node("retrieve", retrieve_node)
builder.add_node("chat", chat_node)
builder.add_node("save", save_node)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "chat")
builder.add_edge("chat", "save")
builder.add_edge("save", END)

graph = builder.compile()

print("Graph Mermaid Representation:")
mermaid_syntax = graph.get_graph().draw_mermaid()
print(mermaid_syntax)

try:
    png_bytes = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(png_bytes)
    print("Saved graph.png successfully via draw_mermaid_png()! Size:", len(png_bytes))
except Exception as e:
    print("draw_mermaid_png failed:", e)
    # Fallback to fetching directly or generating image
    import base64
    graph_bytes = mermaid_syntax.encode('utf-8')
    base64_bytes = base64.b64encode(graph_bytes).decode('utf-8')
    url = f"https://mermaid.ink/img/{base64_bytes}"
    print("Fetching from:", url)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open("graph.png", "wb") as out_file:
        data = response.read()
        out_file.write(data)
    print("Saved graph.png successfully via fallback! Size:", len(data))
