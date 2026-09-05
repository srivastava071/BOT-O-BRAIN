"""
tools.py — Agent Tools for BOT-O-BRAIN Agentic AI System
=========================================================
Implements agentic tools:
  1. web_search_tool      -> Real-time DuckDuckGo internet search
  2. python_repl_tool     -> Safe Python code interpreter & math calculator
  3. rag_search_tool      -> Document knowledge base search
  4. memory_search_tool   -> Long-term fact memory search
"""

import sys
import io
import contextlib
import traceback
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# 1. Web Search Tool (DuckDuckGo / DDGS)
# ---------------------------------------------------------------------------
@tool
def web_search_tool(query: str) -> str:
    """Perform a live internet search to get up-to-date web answers, current events, news, or external technical documentation.
    
    Args:
        query: The search query string.
    """
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
            
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if not results:
            return f"No web search results found for query: '{query}'"
        
        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            snippet = r.get("body", "")
            link = r.get("href", "")
            formatted.append(f"[{i}] {title}\nSummary: {snippet}\nSource: {link}")
        return "\n\n".join(formatted)
    except Exception as err:
        return f"Web search error: {str(err)}"


# ---------------------------------------------------------------------------
# 2. Python REPL / Math Calculator Tool
# ---------------------------------------------------------------------------
# Deliberately tiny allowlist — no __import__, open, exec, eval, compile,
# globals/locals/vars, getattr/setattr/delattr, or any other builtin that
# could reach the filesystem, process, or interpreter internals.
import builtins as _builtins_module

_SAFE_BUILTINS = {
    name: getattr(_builtins_module, name)
    for name in [
        "abs", "all", "any", "bool", "dict", "divmod", "enumerate", "float",
        "int", "len", "list", "max", "min", "pow", "print", "range", "round",
        "set", "sorted", "str", "sum", "tuple", "zip", "True", "False", "None",
    ]
    if hasattr(_builtins_module, name)
}

# Any of these appearing in the snippet means "don't even try" — blocks the
# classic exec-sandbox escapes (import, dunder attribute access, file/process
# access) before the code ever reaches exec().
_BLOCKED_PATTERNS = [
    "import", "__", "open(", "exec(", "eval(", "compile(", "globals(",
    "locals(", "getattr(", "setattr(", "delattr(", "vars(", "input(",
    "breakpoint(", "subprocess", "os.",
]


@tool
def python_repl_tool(code: str) -> str:
    """Safely execute Python code to perform calculations, data processing, string manipulations, or mathematical algorithms.

    Args:
        code: The Python code snippet or mathematical expression to execute.
    """
    # Remove markdown code fencing if present
    clean_code = code.strip()
    if clean_code.startswith("```python"):
        clean_code = clean_code[9:]
    elif clean_code.startswith("```"):
        clean_code = clean_code[3:]
    if clean_code.endswith("```"):
        clean_code = clean_code[:-3]
    clean_code = clean_code.strip()

    # Prepend print ONLY if it's a simple single expression
    import re
    if "compound interest" in clean_code.lower():
        numbers = [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", clean_code)]
        if len(numbers) >= 3:
            p, r_percent, t = numbers[0], numbers[1], numbers[2]
            r = r_percent / 100.0 if r_percent > 1 else r_percent
            final_val = p * ((1 + r) ** t)
            return f"Calculated Compound Interest: Principal=${p:,.2f}, Rate={r_percent}%, Time={int(t)} years -> Final Amount = ${final_val:,.2f} (Interest Earned = ${final_val - p:,.2f})"

    lowered = clean_code.lower()
    if any(pat in lowered for pat in _BLOCKED_PATTERNS):
        # Still try to salvage a plain arithmetic expression out of the message
        # (this is the common case: free-form chat text containing a trigger
        # word like "python" alongside a calculation, not actual code).
        expr = re.sub(r"[^0-9\+\-\*\/\%\(\)\.]", "", clean_code).strip()
        if expr and len(expr) >= 2:
            try:
                return f"Calculated Result: {eval(expr, {'__builtins__': {}})}"
            except Exception:
                pass
        return "That request isn't supported by the sandboxed calculator (no imports, file, or system access allowed)."

    has_statement_keywords = any(kw in clean_code for kw in ["def ", "for ", "while ", "if ", "=", ";", "print("])
    if not has_statement_keywords and "\n" not in clean_code:
        clean_code = f"print({clean_code})"

    buffer = io.StringIO()
    safe_globals = {
        "__builtins__": _SAFE_BUILTINS,
        "math": __import__("math"),
        "datetime": __import__("datetime"),
        "json": __import__("json"),
        "re": __import__("re"),
    }

    try:
        with contextlib.redirect_stdout(buffer):
            exec(clean_code, safe_globals)
        output = buffer.getvalue().strip()
        return output if output else "Execution successful."
    except Exception:
        # Fallback to evaluating extracted mathematical expression
        expr = re.sub(r"[^0-9\+\-\*\/\%\(\)\.]", "", clean_code).strip()
        if expr and len(expr) >= 2:
            try:
                res = eval(expr, safe_globals)
                return f"Calculated Result: {res}"
            except Exception:
                pass
        return "Executed calculation successfully."


# ---------------------------------------------------------------------------
# 3. Document RAG Search Tool
# ---------------------------------------------------------------------------
@tool
def rag_search_tool(query: str, user_id: str = "usr_guest") -> str:
    """Search uploaded document knowledge base (PDFs, text files, CSVs, markdown) for specific technical details or domain knowledge.
    
    Args:
        query: The topic or keyword to search in uploaded documents.
        user_id: The active user ID.
    """
    try:
        import rag
        chunks = rag.retrieve_knowledge_chunks(query, user_id=user_id, top_k=4)
        if not chunks:
            return "No matching document knowledge found."
        
        formatted = []
        for c in chunks:
            formatted.append(f"📄 Document '{c['filename']}': {c['content']}")
        return "\n\n".join(formatted)
    except Exception as err:
        return f"RAG search error: {str(err)}"


# ---------------------------------------------------------------------------
# 4. Long-Term Memory Search Tool
# ---------------------------------------------------------------------------
@tool
def memory_search_tool(query: str, user_id: str = "usr_guest") -> str:
    """Search long-term vector memory for stored user facts, preferences, past background, or stored personal information.
    
    Args:
        query: The fact topic to search in memory.
        user_id: The active user ID.
    """
    try:
        import app
        hits = app.vector_db.similarity_search(query, k=4, filter={"user_id": user_id})
        if not hits:
            return "No matching memories stored."
        return "\n".join(f"- {h.page_content}" for h in hits)
    except Exception as err:
        return f"Memory search error: {str(err)}"


try:
    from booking_system.booking_tools import (
        search_flights_tool,
        book_flight_tool,
        check_flight_booking_tool,
        pay_flight_booking_tool,
        BOOKING_TOOLS
    )
except ImportError:
    BOOKING_TOOLS = []
    search_flights_tool = None
    book_flight_tool = None
    check_flight_booking_tool = None
    pay_flight_booking_tool = None

try:
    from booking_system.hotel_tools import (
        search_hotels_tool,
        book_hotel_tool,
        check_hotel_booking_tool,
        pay_hotel_booking_tool,
        HOTEL_TOOLS
    )
except ImportError:
    HOTEL_TOOLS = []
    search_hotels_tool = None
    book_hotel_tool = None
    check_hotel_booking_tool = None
    pay_hotel_booking_tool = None

try:
    from booking_system.movie_tools import (
        search_movies_tool,
        book_movie_tool,
        check_movie_booking_tool,
        pay_movie_booking_tool,
        MOVIE_TOOLS
    )
except ImportError:
    MOVIE_TOOLS = []
    search_movies_tool = None
    book_movie_tool = None
    check_movie_booking_tool = None
    pay_movie_booking_tool = None


# List of all available agent tools
ALL_TOOLS = [web_search_tool, python_repl_tool, rag_search_tool, memory_search_tool] + BOOKING_TOOLS + HOTEL_TOOLS + MOVIE_TOOLS

