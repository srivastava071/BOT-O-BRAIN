"""
main.py — Agentic Memory & Tool-Using Chatbot
=============================================

A LangGraph Agentic AI Assistant featuring:
  * AGENTIC TOOLS    -> Web Search (DuckDuckGo), Python REPL / Calculator, Document RAG, Vector Memory
  * SHORT-TERM memory-> LangGraph MemorySaver checkpointer (per thread_id)
  * LONG-TERM memory -> Chroma vector DB (persists to ./vector_db)

Flow each turn:  retrieve -> agent_reasoning (with tool calling) -> tool_exec -> chat -> save -> END
"""

from __future__ import annotations

import os
import uuid
import json
from typing import Annotated, List, Optional, TypedDict, Dict, Any

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
try:
    from langchain_chroma import Chroma
except Exception:
    from langchain_community.vectorstores import Chroma

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

import tools

load_dotenv()

# ---------------------------------------------------------------------------
# 1. Models: chat (Groq/OpenAI) + embeddings (OpenAI or local)
# ---------------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

_GROQ_LLM = (
    ChatOpenAI(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        max_retries=1,
    )
    if GROQ_API_KEY
    else None
)

_GROQ_FAST_LLM = (
    ChatOpenAI(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        max_retries=1,
    )
    if GROQ_API_KEY
    else None
)

_GROQ_VISION_LLM = (
    ChatOpenAI(
        model="llama-3.2-11b-vision-preview",
        temperature=0.2,
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        max_retries=1,
    )
    if GROQ_API_KEY
    else None
)

_GROQ_VISION_90B_LLM = (
    ChatOpenAI(
        model="llama-3.2-90b-vision-preview",
        temperature=0.2,
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        max_retries=1,
    )
    if GROQ_API_KEY
    else None
)

_OPENROUTER_LLM = (
    ChatOpenAI(
        model="deepseek/deepseek-r1:free",
        temperature=0.3,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        max_retries=1,
    )
    if OPENROUTER_API_KEY
    else None
)

_OPENROUTER_VISION_LLM = (
    ChatOpenAI(
        model="google/gemini-2.5-flash:free",
        temperature=0.2,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        max_retries=1,
    )
    if OPENROUTER_API_KEY
    else None
)

_COHERE_LLM = (
    ChatOpenAI(
        model="command-r-plus",
        temperature=0.3,
        api_key=COHERE_API_KEY,
        base_url="https://api.cohere.com/v2",
        max_retries=1,
    )
    if COHERE_API_KEY
    else None
)

_OPENAI_LLM = (
    ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)


def has_image_message(messages: List[BaseMessage]) -> bool:
    """Check if any message contains multi-modal image content."""
    for m in messages:
        if isinstance(m.content, list):
            for part in m.content:
                if isinstance(part, dict) and part.get("type") == "image_url":
                    return True
    return False


def clean_messages_for_text_llm(messages: List[BaseMessage]) -> List[BaseMessage]:
    """Convert multi-modal image payloads into clean text messages for text-only LLMs."""
    cleaned = []
    for m in messages:
        if isinstance(m.content, list):
            text_parts = []
            for part in m.content:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    elif part.get("type") == "image_url":
                        text_parts.append("[Image attached]")
            cleaned.append(type(m)(content=" ".join(text_parts)))
        else:
            cleaned.append(m)
    return cleaned


def trim_messages_window(messages: List[BaseMessage], max_messages: int = 10) -> List[BaseMessage]:
    """Ensures LLM prompts never exceed model context window limits."""
    if len(messages) <= max_messages:
        return messages
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    non_system_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
    recent_msgs = non_system_msgs[-max_messages:]
    return system_msgs + recent_msgs


def invoke_llm(messages: List[BaseMessage], fast: bool = False) -> BaseMessage:
    """Intelligent fallback across Groq -> OpenRouter -> Cohere -> OpenAI."""
    messages = trim_messages_window(messages, max_messages=10)
    has_image = has_image_message(messages)
    errors = []

    # 1. Vision LLM if image is attached
    if has_image:
        if _GROQ_VISION_90B_LLM:
            try:
                return _GROQ_VISION_90B_LLM.invoke(messages)
            except Exception as err:
                errors.append(f"Groq Vision 90B: {err}")
        if _GROQ_VISION_LLM:
            try:
                return _GROQ_VISION_LLM.invoke(messages)
            except Exception as err:
                errors.append(f"Groq Vision 11B: {err}")
        if _OPENROUTER_VISION_LLM:
            try:
                return _OPENROUTER_VISION_LLM.invoke(messages)
            except Exception as err:
                errors.append(f"OpenRouter Vision: {err}")

    # 2. Try Fast Groq 8B, fallback to 70B
    if GROQ_API_KEY:
        llm_input = clean_messages_for_text_llm(messages) if has_image else messages
        if fast and _GROQ_FAST_LLM:
            try:
                return _GROQ_FAST_LLM.invoke(llm_input)
            except Exception as err:
                errors.append(f"Groq 8B: {err}")
        if _GROQ_LLM:
            try:
                return _GROQ_LLM.invoke(llm_input)
            except Exception as err:
                errors.append(f"Groq 70B: {err}")

    # 3. OpenRouter
    if _OPENROUTER_LLM:
        try:
            llm_input = clean_messages_for_text_llm(messages) if has_image else messages
            return _OPENROUTER_LLM.invoke(llm_input)
        except Exception as err:
            errors.append(f"OpenRouter: {err}")

    # 4. Cohere
    if _COHERE_LLM:
        try:
            llm_input = clean_messages_for_text_llm(messages) if has_image else messages
            return _COHERE_LLM.invoke(llm_input)
        except Exception as err:
            errors.append(f"Cohere: {err}")

    # 5. OpenAI
    if _OPENAI_LLM:
        try:
            return _OPENAI_LLM.invoke(messages)
        except Exception as err:
            errors.append(f"OpenAI: {err}")

    raise RuntimeError(f"All LLM providers failed: {errors}")


_EMBEDDINGS_INSTANCE = None


def make_embeddings():
    """Embeddings singleton."""
    global _EMBEDDINGS_INSTANCE
    if _EMBEDDINGS_INSTANCE is not None:
        return _EMBEDDINGS_INSTANCE

    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-proj-"):
        try:
            from langchain_openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small", api_key=OPENAI_API_KEY
            )
            _EMBEDDINGS_INSTANCE = embeddings
            return _EMBEDDINGS_INSTANCE
        except Exception:
            pass

    from langchain_huggingface import HuggingFaceEmbeddings

    _EMBEDDINGS_INSTANCE = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _EMBEDDINGS_INSTANCE


def make_llm():
    """Returns the primary active LLM instance (Groq -> OpenAI -> OpenRouter -> Cohere)."""
    return _GROQ_LLM or _OPENAI_LLM or _OPENROUTER_LLM or _COHERE_LLM

llm = make_llm()

# Long-term memory store
vector_db = Chroma(
    collection_name="long_term_memory",
    embedding_function=make_embeddings(),
    persist_directory="./vector_db",
)


# ---------------------------------------------------------------------------
# 2. Graph state
# ---------------------------------------------------------------------------
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    memories: List[str]
    user_id: Optional[str]
    chat_mode: Optional[str]  # "full" vs "memory_only"
    assistant_type: Optional[str]  # "general" vs "flight"
    executed_tools: List[Dict[str, Any]]  # Live tool trace metadata for UI


# ---------------------------------------------------------------------------
# 3. Prompts
# ---------------------------------------------------------------------------
CHAT_PROMPT = """You are BOT-O-BRAIN, an Agentic AI Assistant equipped with:
  - Flight Ticket Booking & Reservation System (Search, PNR reservation, status check, payment confirmation)
  - Real-time Web Search (DuckDuckGo)
  - Python Code Interpreter & Calculator
  - Document Knowledge Base RAG
  - Long-term Memory Storage

Formatting & Response Guidelines:
1. Provide clean, well-structured, and concise responses.
2. When booking a flight ticket or searching for flights, provide clear PNR codes, fare details, and payment instructions.
3. Use bold titles, bullet points, or code blocks where appropriate.
4. Be direct, clear, and easy to read.

Retrieved Context Memories & Document Knowledge:
{memories}
"""

FLIGHT_CHAT_PROMPT = """You are SkyBot, the Dedicated Flight AI Concierge of BOT-O-BRAIN.
Your sole purpose is assisting users with live flight searches (Google Flights), PNR reservations, flight status checks, and e-ticket payment confirmations.

Flight Assistant Guidelines:
1. Provide clear flight comparisons (Airline, Flight Code, Departure/Arrival times, Fares in INR).
2. When reserving seats, generate distinct PNR codes and present fare totals clearly.
3. Keep answers friendly, professional, and aviation-themed.

Retrieved Context Memories:
{memories}
"""


EXTRACT_PROMPT = """Extract durable, long-term facts about the USER from this exchange
(name, preferences, goals, profession, location, favourite tech, projects, interests).
Ignore greetings, small talk, and one-off questions.

Output one fact per line, or exactly NONE if there is nothing worth remembering.

User: {user}
Assistant: {assistant}

Facts:"""


# ---------------------------------------------------------------------------
# 4. Nodes
# ---------------------------------------------------------------------------
def last_of(messages: List[BaseMessage], kind) -> str:
    """Return the text of the most recent message of the given class."""
    for m in reversed(messages):
        if isinstance(m, kind):
            return str(m.content)
    return ""


def is_guest(user_id: Optional[str]) -> bool:
    """Helper checking if user is an unauthenticated guest."""
    if not user_id or user_id == "usr_guest" or "guest" in str(user_id).lower():
        return True
    return False


def retrieve_node(state: State) -> dict:
    """Find long-term memories + RAG knowledge chunks relevant to latest user message."""
    user_id = state.get("user_id") or "usr_guest"
    
    # GUEST MODE: Disable long-term memory & RAG document retrieval for guests
    if is_guest(user_id):
        return {"memories": [], "executed_tools": state.get("executed_tools") or []}

    query = last_of(state["messages"], HumanMessage)
    filter_dict = {"user_id": user_id}

    memories = []
    chat_mode = state.get("chat_mode") or "full"

    # 1. Retrieve user personal memories (if in 'full' or 'memory_only' mode)
    if chat_mode in ("full", "memory_only"):
        try:
            hits = vector_db.similarity_search(query, k=3, filter=filter_dict) if query else []
            for h in hits:
                memories.append(h.page_content)
        except Exception:
            pass

    # 2. Retrieve RAG Knowledge Base document chunks (if in 'full' or 'rag_only' mode)
    if chat_mode in ("full", "rag_only"):
        try:
            import rag
            rag_chunks = rag.retrieve_knowledge_chunks(query, user_id=user_id, top_k=4)
            for chunk in rag_chunks:
                memories.append(f"[Document Knowledge '{chunk['filename']}']: {chunk['content']}")
        except Exception as _r_err:
            pass

    return {"memories": memories, "executed_tools": state.get("executed_tools") or []}


def chat_node(state: State) -> dict:
    """Agent Reasoning Node: Evaluates prompt, decides if tools or calculations are needed."""
    user_msg = last_of(state["messages"], HumanMessage).strip()
    executed_tools = list(state.get("executed_tools") or [])

    # Check triggers
    math_triggers = ["calculate", "math", "sqrt", "compound interest", "python", "code", "factorial", "evaluate"]
    web_triggers = ["weather", "today", "news", "current price", "who is current", "latest documentation"]
    flight_triggers = ["flight", "book flight", "ticket", "book ticket", "delhi to", "mumbai to", "pnr-", "pay pnr", "pay flight"]

    tool_outputs = []

    # 1. Execute Flight Booking tools if requested
    if any(trig in user_msg.lower() for trig in flight_triggers):
        try:
            if hasattr(tools, "book_flight_tool") and tools.book_flight_tool:
                user_id = state.get("user_id") or "usr_guest"
                msg_lower = user_msg.lower()
                
                # Payment flow
                if "pay" in msg_lower and "pnr" in msg_lower:
                    import re
                    pnr_match = re.search(r"PNR-BOB\d+", user_msg, re.IGNORECASE)
                    if pnr_match:
                        pnr = pnr_match.group(0).upper()
                        pay_res = tools.pay_flight_booking_tool.invoke({"pnr": pnr, "payment_method": "UPI", "user_id": user_id})
                        tool_outputs.append(f"Flight Payment Execution: {pay_res}")
                        executed_tools.append({"tool": "pay_flight_booking", "query": user_msg, "result": str(pay_res)[:200]})
                
                # Check status flow
                elif "pnr" in msg_lower and ("status" in msg_lower or "check" in msg_lower):
                    import re
                    pnr_match = re.search(r"PNR-BOB\d+", user_msg, re.IGNORECASE)
                    if pnr_match:
                        pnr = pnr_match.group(0).upper()
                        status_res = tools.check_flight_booking_tool.invoke({"pnr": pnr, "user_id": user_id})
                        tool_outputs.append(f"Flight Booking Status: {status_res}")
                        executed_tools.append({"tool": "check_flight_booking", "query": user_msg, "result": str(status_res)[:200]})

                # Book flight flow
                elif "book" in msg_lower or "reserve" in msg_lower:
                    import re
                    # Parse origin and destination if possible
                    cities = ["delhi", "mumbai", "bengaluru", "bangalore", "goa", "hyderabad", "kolkata", "chennai", "pune", "jaipur", "ahmedabad"]
                    found_cities = [c.capitalize() for c in cities if c in msg_lower]
                    orig = found_cities[0] if len(found_cities) > 0 else "Delhi"
                    dest = found_cities[1] if len(found_cities) > 1 else "Mumbai"
                    
                    booking_res = tools.book_flight_tool.invoke({
                        "origin": orig,
                        "destination": dest,
                        "travel_date": "2026-07-26",
                        "passenger_name": "Priyanshu",
                        "user_id": user_id
                    })
                    tool_outputs.append(f"Flight Reservation Result:\n{booking_res}")
                    executed_tools.append({"tool": "book_flight", "query": user_msg, "result": str(booking_res)[:200]})

                # Search flight flow
                elif "search" in msg_lower or "available" in msg_lower or "flights" in msg_lower:
                    search_res = tools.search_flights_tool.invoke({"origin": "Delhi", "destination": "Mumbai", "travel_date": "2026-07-26"})
                    tool_outputs.append(f"Flight Search Results:\n{search_res}")
                    executed_tools.append({"tool": "search_flights", "query": user_msg, "result": str(search_res)[:200]})
        except Exception as f_err:
            print(f"[DEBUG] Flight tool trigger error: {f_err}")

    # 2. Execute Hotel Booking tools if requested
    hotel_triggers = ["hotel", "room", "suite", "resort", "book hotel", "reserve hotel", "cheapest hotel", "cheap hotel", "stay", "taj", "leela", "pnr-htl"]
    if any(trig in user_msg.lower() for trig in hotel_triggers):
        try:
            if hasattr(tools, "book_hotel_tool") and tools.book_hotel_tool:
                user_id = state.get("user_id") or "usr_guest"
                msg_lower = user_msg.lower()
                
                # Payment flow
                if "pay" in msg_lower and ("pnr" in msg_lower or "htl" in msg_lower):
                    import re
                    pnr_match = re.search(r"PNR-HTL\d+", user_msg, re.IGNORECASE)
                    if pnr_match:
                        pnr = pnr_match.group(0).upper()
                        pay_res = tools.pay_hotel_booking_tool.invoke({"pnr": pnr, "payment_method": "UPI", "user_id": user_id})
                        tool_outputs.append(f"Hotel Payment Execution: {pay_res}")
                        executed_tools.append({"tool": "pay_hotel_booking", "query": user_msg, "result": str(pay_res)[:200]})

                # Status flow
                elif ("pnr-htl" in msg_lower or "htl" in msg_lower) and ("status" in msg_lower or "check" in msg_lower):
                    import re
                    pnr_match = re.search(r"PNR-HTL\d+", user_msg, re.IGNORECASE)
                    if pnr_match:
                        pnr = pnr_match.group(0).upper()
                        status_res = tools.check_hotel_booking_tool.invoke({"pnr": pnr, "user_id": user_id})
                        tool_outputs.append(f"Hotel Reservation Status: {status_res}")
                        executed_tools.append({"tool": "check_hotel_booking", "query": user_msg, "result": str(status_res)[:200]})

                # Book room flow
                elif any(k in msg_lower for k in ["book", "reserve", "confirm"]):
                    cities = ["goa", "mumbai", "delhi", "bengaluru", "jaipur", "udaipur", "manali", "shimla"]
                    found = [c for c in cities if c in msg_lower]
                    target_city = found[0].capitalize() if found else "Delhi"
                    
                    h_name = None
                    if "cheap" in msg_lower or "budget" in msg_lower:
                        h_name = "Ginger Hotel" if target_city == "Delhi" else "Bloomrooms"

                    hotel_res = tools.book_hotel_tool.invoke({
                        "city": target_city,
                        "guest_name": "Priyanshu",
                        "hotel_name": h_name,
                        "check_in": "Tomorrow",
                        "user_id": user_id
                    })
                    tool_outputs.append(f"Hotel Reservation Result:\n{hotel_res}")
                    executed_tools.append({"tool": "book_hotel", "query": user_msg, "result": str(hotel_res)[:200]})

                # Search hotel flow
                elif any(k in msg_lower for k in ["search", "recommend", "hotels", "cheapest", "cheap", "find", "hotel"]):
                    cities = ["goa", "mumbai", "delhi", "bengaluru", "jaipur", "udaipur", "manali", "shimla"]
                    found = [c for c in cities if c in msg_lower]
                    target_city = found[0].capitalize() if found else "Delhi"
                    sort_mode = "cheapest" if any(k in msg_lower for k in ["cheap", "cheapest", "budget", "lowest", "value"]) else "default"
                    
                    search_res = tools.search_hotels_tool.invoke({"city": target_city, "sort_by": sort_mode})
                    tool_outputs.append(f"Hotel Search Results:\n{search_res}")
                    executed_tools.append({"tool": "search_hotels", "query": user_msg, "result": str(search_res)[:200]})
        except Exception as h_err:
            print(f"[DEBUG] Hotel tool trigger error: {h_err}")

    # 3. Execute Movie Ticket tools if requested
    movie_triggers = ["movie", "cinema", "showtime", "ticket", "imax", "pvr", "inox", "book movie", "pnr-mov"]
    if any(trig in user_msg.lower() for trig in movie_triggers):
        try:
            if hasattr(tools, "book_movie_tool") and tools.book_movie_tool:
                user_id = state.get("user_id") or "usr_guest"
                msg_lower = user_msg.lower()
                
                # Payment flow
                if "pay" in msg_lower and ("pnr" in msg_lower or "mov" in msg_lower):
                    import re
                    pnr_match = re.search(r"PNR-MOV\d+", user_msg, re.IGNORECASE)
                    if pnr_match:
                        pnr = pnr_match.group(0).upper()
                        pay_res = tools.pay_movie_booking_tool.invoke({"pnr": pnr, "payment_method": "UPI", "user_id": user_id})
                        tool_outputs.append(f"Movie Ticket Payment: {pay_res}")
                        executed_tools.append({"tool": "pay_movie_booking", "query": user_msg, "result": str(pay_res)[:200]})

                # Status flow
                elif ("pnr-mov" in msg_lower or "mov" in msg_lower) and ("status" in msg_lower or "check" in msg_lower):
                    import re
                    pnr_match = re.search(r"PNR-MOV\d+", user_msg, re.IGNORECASE)
                    if pnr_match:
                        pnr = pnr_match.group(0).upper()
                        status_res = tools.check_movie_booking_tool.invoke({"pnr": pnr, "user_id": user_id})
                        tool_outputs.append(f"Movie Ticket Status: {status_res}")
                        executed_tools.append({"tool": "check_movie_booking", "query": user_msg, "result": str(status_res)[:200]})

                # Book movie ticket flow
                elif "book" in msg_lower or "reserve" in msg_lower or "ticket" in msg_lower:
                    m_title = "Avatar: Fire & Ash"
                    if "pushpa" in msg_lower: m_title = "Pushpa 2: The Rule"
                    elif "dune" in msg_lower: m_title = "Dune: Part Two"
                    elif "stree" in msg_lower: m_title = "Stree 2"
                    
                    movie_res = tools.book_movie_tool.invoke({
                        "movie_title": m_title,
                        "customer_name": "Priyanshu",
                        "city": "Delhi",
                        "tickets_count": 2,
                        "user_id": user_id
                    })
                    tool_outputs.append(f"Movie Ticket Reservation Result:\n{movie_res}")
                    executed_tools.append({"tool": "book_movie", "query": user_msg, "result": str(movie_res)[:200]})

                # Search movie flow
                elif "search" in msg_lower or "showing" in msg_lower or "movies" in msg_lower:
                    search_res = tools.search_movies_tool.invoke({"city": "Delhi"})
                    tool_outputs.append(f"Movie Search Results:\n{search_res}")
                    executed_tools.append({"tool": "search_movies", "query": user_msg, "result": str(search_res)[:200]})
        except Exception as m_err:
            print(f"[DEBUG] Movie tool trigger error: {m_err}")

    # 2. Execute Python REPL if math/code is requested
    if any(trig in user_msg.lower() for trig in math_triggers):
        try:
            repl_result = tools.python_repl_tool.invoke(user_msg)
            tool_outputs.append(f"Python Execution Result: {repl_result}")
            executed_tools.append({"tool": "python_repl", "query": user_msg, "result": str(repl_result)[:200]})
        except Exception as err:
            pass

    # 3. Execute Web Search if real-time web info is requested
    if any(trig in user_msg.lower() for trig in web_triggers):
        try:
            search_result = tools.web_search_tool.invoke(user_msg)
            tool_outputs.append(f"Web Search Results:\n{search_result}")
            executed_tools.append({"tool": "web_search", "query": user_msg, "result": str(search_result)[:200]})
        except Exception as err:
            pass


    # Build final combined context
    all_context = list(state["memories"]) + tool_outputs
    mem_text = "\n".join(f"- {m}" for m in all_context) or "(none yet)"
    
    assistant_type = state.get("assistant_type") or "general"
    prompt_template = FLIGHT_CHAT_PROMPT if assistant_type == "flight" else CHAT_PROMPT
    system = SystemMessage(content=prompt_template.format(memories=mem_text))
    
    reply = invoke_llm([system] + state["messages"])
    return {"messages": [reply], "executed_tools": executed_tools}



TRIVIAL_WORDS = {"hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "cool", "bye", "exit", "quit", "yes", "no"}


def save_node(state: State) -> dict:
    """Ask the fast LLM what (if anything) to remember, then store it in Chroma."""
    user_id = state.get("user_id") or "usr_guest"

    # GUEST MODE SAFETY: In Guest mode, NEVER extract or store facts into Chroma DB.
    if is_guest(user_id):
        return {}

    user = last_of(state["messages"], HumanMessage).strip()
    assistant = last_of(state["messages"], AIMessage).strip()

    if not user or len(user) < 6 or user.lower() in TRIVIAL_WORDS:
        return {}

    prompt = EXTRACT_PROMPT.format(user=user, assistant=assistant)
    extracted = str(invoke_llm([HumanMessage(content=prompt)], fast=True).content).strip()

    if extracted and extracted.upper() != "NONE":
        new_facts = []
        for line in extracted.splitlines():
            fact = line.lstrip("-• ").strip()
            if fact and fact.upper() != "NONE":
                new_facts.append(fact)
        if new_facts:
            ids = [str(uuid.uuid4()) for _ in new_facts]
            metadatas = [{"user_id": user_id}] * len(new_facts)
            vector_db.add_texts(new_facts, ids=ids, metadatas=metadatas)
            for f in new_facts:
                print(f"   [memory saved for user {user_id}] {f}")
    return {}


# ---------------------------------------------------------------------------
# 5. Build graph: START -> retrieve -> chat -> save -> END
# ---------------------------------------------------------------------------
builder = StateGraph(State)
builder.add_node("retrieve", retrieve_node)
builder.add_node("chat", chat_node)
builder.add_node("save", save_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "chat")
builder.add_edge("chat", "save")
builder.add_edge("save", END)

graph = builder.compile(checkpointer=MemorySaver())


def main() -> None:
    thread_id = "demo-session"
    config = {"configurable": {"thread_id": thread_id}}

    print("BOT-O-BRAIN Agentic AI System ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        if not user_input:
            continue

        result = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]}, config=config
        )
        print(f"Bot: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    main()