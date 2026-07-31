"""
server.py — FastAPI Backend for Memory Chatbot (Secure Auth Edition)
=====================================================================

Provides REST API endpoints for secure user signup, email OTP verification,
dual email/username login, multi-tenant chat sessions, and user-isolated Chroma DB memories.
"""

import sys
import os
import uuid
import warnings
from typing import List, Optional

# Windows' console defaults to the cp1252 codepage, which cannot encode
# many characters this app prints in debug/log statements (₹, emoji, etc.).
# That raised UnicodeEncodeError deep inside a background graph node and
# crashed the whole /api/chat request with a 500 — e.g. every flight search
# that saved a fact mentioning a ₹ price. Force UTF-8 stdio so a print()
# never takes the request down.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import io
import base64
import pypdf

from fastapi import FastAPI, HTTPException, Request, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

warnings.filterwarnings("ignore")

from app import graph, vector_db, llm, HumanMessage, AIMessage
import storage
import rag
from mailer import send_otp_email

app = FastAPI(title="Memory Chatbot Multi-User API", version="1.3.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignupRequest(BaseModel):
    full_name: str
    email: str
    username: str
    password: str
    confirm_password: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp_code: str

class ResendOtpRequest(BaseModel):
    email: str

class LoginRequest(BaseModel):
    login_identifier: str
    password: str

class Attachment(BaseModel):
    filename: str
    file_type: str  # "image" | "pdf" | "document"
    content_type: str
    data: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    chat_mode: Optional[str] = "full"  # "full" vs "memory_only"
    assistant_type: Optional[str] = "general"  # "general" vs "flight"
    attachment: Optional[Attachment] = None



class MemoryCreateRequest(BaseModel):
    text: str

class RenameSessionRequest(BaseModel):
    title: str


def get_current_user_id(request: Request) -> str:
    user_id = request.headers.get("X-User-Id")
    if user_id:
        user = storage.get_user_by_id(user_id)
        if user:
            return user["id"]
    
    # Check/create default guest user
    try:
        conn = storage.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'guest'")
        row = cursor.fetchone()
        if row:
            return row["id"]
        else:
            reg = storage.register_user("Guest User", "guest@memorybot.com", "guest", "guest123")
            storage.get_connection().execute("UPDATE users SET is_verified = 1 WHERE username = 'guest'")
            return reg["id"]
    except Exception:
        return "usr_guest"


def is_guest_user(user_id: str) -> bool:
    """Returns True if the given user_id corresponds to an unauthenticated guest."""
    if not user_id or user_id == "usr_guest":
        return True
    try:
        user = storage.get_user_by_id(user_id)
        if user and user.get("username") == "guest":
            return True
    except Exception:
        pass
    return False


def ensure_graph_hydrated(session_id: str, user_id: str):
    """Ensures LangGraph's checkpointer state has the full message history for thread_id."""
    config = {"configurable": {"thread_id": session_id}}
    try:
        current_state = graph.get_state(config)
        if not current_state.values or "messages" not in current_state.values or not current_state.values["messages"]:
            history = storage.get_session_messages(session_id, user_id=user_id)
            langchain_msgs = []
            for m in history:
                if m["role"] == "user":
                    langchain_msgs.append(HumanMessage(content=m["content"]))
                elif m["role"] == "bot":
                    langchain_msgs.append(AIMessage(content=m["content"]))
            if langchain_msgs:
                graph.update_state(config, {"messages": langchain_msgs})
    except Exception as e:
        print(f"Warning hydrating graph state for {session_id}: {e}")


# =========================================================================
# SECURE AUTHENTICATION ENDPOINTS
# =========================================================================

@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Password and Confirm Password do not match.")

    try:
        result = storage.register_user(
            full_name=req.full_name,
            email=req.email,
            username=req.username,
            password=req.password
        )
        otp_code = result.get("otp_demo")
        email_sent = send_otp_email(req.email, otp_code, req.full_name)
        return {
            "status": "otp_sent",
            "message": f"6-digit verification OTP code sent directly to {req.email}",
            "email": req.email,
            "email_sent": email_sent,
            "otp_demo": otp_code
        }
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/auth/verify-otp")
async def verify_otp(req: VerifyOtpRequest):
    try:
        user = storage.verify_email_otp(req.email, req.otp_code)
        return {"status": "success", "user": user, "message": "Email verified successfully!"}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/auth/resend-otp")
async def resend_otp(req: ResendOtpRequest):
    try:
        new_otp = storage.resend_otp(req.email)
        email_sent = send_otp_email(req.email, new_otp)
        return {
            "status": "success",
            "message": f"New OTP verification code sent directly to {req.email}",
            "email_sent": email_sent,
            "otp_demo": new_otp
        }
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    try:
        user = storage.login_user(req.login_identifier, req.password)
        return {"status": "success", "user": user}
    except ValueError as err:
        raise HTTPException(status_code=401, detail=str(err))


@app.get("/api/auth/me")
async def get_me(request: Request):
    user_id = get_current_user_id(request)
    user = storage.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


# =========================================================================
# SESSIONS ENDPOINTS (USER-SCOPED)
# =========================================================================

@app.get("/api/sessions")
async def list_sessions(request: Request, assistant_type: Optional[str] = None):
    user_id = get_current_user_id(request)
    sessions = storage.get_all_sessions(user_id, assistant_type=assistant_type)
    return {"sessions": sessions}


@app.post("/api/sessions")
async def create_new_session(request: Request, assistant_type: str = "general"):
    user_id = get_current_user_id(request)
    session = storage.create_session(user_id=user_id, assistant_type=assistant_type)
    return session


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request):
    user_id = get_current_user_id(request)
    session = storage.get_session(session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = storage.get_session_messages(session_id, user_id=user_id)
    ensure_graph_hydrated(session_id, user_id)
    return {"session": session, "messages": messages}


@app.delete("/api/sessions/{session_id}")
async def delete_session_endpoint(session_id: str, request: Request):
    user_id = get_current_user_id(request)
    session = storage.get_session(session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    storage.delete_session(session_id, user_id=user_id)
    return {"status": "deleted", "id": session_id}


@app.patch("/api/sessions/{session_id}")
async def rename_session_endpoint(session_id: str, req: RenameSessionRequest, request: Request):
    user_id = get_current_user_id(request)
    new_title = req.title.strip()
    if not new_title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    storage.update_session_title(session_id, new_title, user_id=user_id)
    return {"status": "updated", "id": session_id, "title": new_title}


# =========================================================================
# CHAT WORKFLOW ENDPOINT (USER-SCOPED)
# =========================================================================

@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        filename = file.filename or "uploaded_file"
        content_type = file.content_type or ""
        ext = filename.split(".")[-1].lower() if "." in filename else ""

        if content_type.startswith("image/") or ext in ("png", "jpg", "jpeg", "webp"):
            b64 = base64.b64encode(contents).decode("utf-8")
            data_uri = f"data:{content_type or 'image/png'};base64,{b64}"
            return {
                "filename": filename,
                "file_type": "image",
                "content_type": content_type,
                "data": data_uri
            }
        elif ext == "pdf" or content_type == "application/pdf":
            try:
                reader = pypdf.PdfReader(io.BytesIO(contents))
                text_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                extracted_text = "\n".join(text_pages).strip()
                if not extracted_text:
                    extracted_text = "(PDF uploaded, but contains scanned images or no extractable text)"
            except Exception as e:
                extracted_text = f"(Error reading PDF: {e})"
            return {
                "filename": filename,
                "file_type": "pdf",
                "content_type": content_type,
                "data": extracted_text
            }
        else:
            try:
                text = contents.decode("utf-8", errors="ignore").strip()
            except Exception:
                text = "(Binary file content)"
            return {
                "filename": filename,
                "file_type": "document",
                "content_type": content_type,
                "data": text
            }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"File upload error: {err}")


# =========================================================================
# DOCUMENT KNOWLEDGE BASE RAG ENDPOINTS (USER-SCOPED)
# =========================================================================

@app.post("/api/rag/upload")
async def rag_upload_document(request: Request, file: UploadFile = File(...)):
    """Ingests document into user's RAG Vector Knowledge Base."""
    user_id = get_current_user_id(request)
    if is_guest_user(user_id):
        raise HTTPException(
            status_code=401,
            detail="Sign in required to upload documents to Knowledge Base. Please sign in or create an account."
        )
    contents = await file.read()
    filename = file.filename or "uploaded_knowledge_file"
    content_type = file.content_type or ""

    result = rag.ingest_document(
        contents=contents,
        filename=filename,
        content_type=content_type,
        user_id=user_id
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.get("/api/rag/documents")
async def rag_list_documents(request: Request):
    """Lists ingested knowledge documents for the current user."""
    user_id = get_current_user_id(request)
    docs = rag.list_user_documents(user_id)
    return {"documents": docs, "total": len(docs)}


@app.delete("/api/rag/documents/{filename:path}")
async def rag_delete_document(filename: str, request: Request):
    """Deletes all vector chunks of a document for current user."""
    user_id = get_current_user_id(request)
    success = rag.delete_user_document(filename=filename, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found.")
    return {"status": "success", "message": f"Deleted '{filename}' from Knowledge Base."}


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    user_id = get_current_user_id(request)
    user_input = req.message.strip()
    if not user_input and not req.attachment:
        raise HTTPException(status_code=400, detail="Message or attachment cannot be empty")

    if not user_input and req.attachment:
        user_input = f"Analyzed attachment: {req.attachment.filename}"

    assistant_type = req.assistant_type or "general"

    session_id = req.session_id
    if not session_id or not storage.get_session(session_id, user_id=user_id):
        session = storage.create_session(user_id=user_id, session_id=session_id, assistant_type=assistant_type)
        session_id = session["id"]

    ensure_graph_hydrated(session_id, user_id)
    
    # Build LangChain HumanMessage payload (Text vs Vision vs Document)
    if req.attachment and req.attachment.file_type == "image":
        human_msg = HumanMessage(content=[
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": req.attachment.data}}
        ])
    elif req.attachment and req.attachment.file_type in ("pdf", "document"):
        doc_header = f"\n\n[Uploaded File '{req.attachment.filename}']:\n{req.attachment.data[:6000]}"
        human_msg = HumanMessage(content=user_input + doc_header)
    else:
        human_msg = HumanMessage(content=user_input)

    config = {"configurable": {"thread_id": session_id}}
    
    try:
        before_count = vector_db._collection.count()
    except Exception:
        before_count = 0

    result = graph.invoke(
        {"messages": [human_msg], "user_id": user_id, "chat_mode": req.chat_mode or "full", "assistant_type": assistant_type},
        config=config
    )



    # Store clean human message in database after invocation
    display_content = user_input
    if req.attachment:
        display_content = f"{user_input}\n📎 [{req.attachment.file_type.upper()}: {req.attachment.filename}]"

    storage.add_message(session_id=session_id, user_id=user_id, role="user", content=display_content, assistant_type=assistant_type)

    bot_reply = result["messages"][-1].content
    raw_memories = result.get("memories", [])
    
    # Format retrieved memories cleanly for UI display (prevent raw document chunk dump)
    clean_memories = []
    seen_rag_files = set()
    for m in raw_memories:
        if m.startswith("[Document Knowledge '"):
            try:
                fname = m.split("'")[1]
                if fname not in seen_rag_files:
                    seen_rag_files.add(fname)
                    clean_memories.append(f"📄 Document: {fname}")
            except Exception:
                clean_memories.append("📄 Knowledge Document")
        else:
            clean_memories.append(m)

    retrieved_memories = clean_memories
    executed_tools = result.get("executed_tools", [])

    new_facts = []
    try:
        after_count = vector_db._collection.count()
        if after_count > before_count:
            coll = vector_db._collection.get(where={"user_id": user_id}, include=["documents"])
            if coll and "documents" in coll and coll["documents"]:
                new_facts = coll["documents"][- (after_count - before_count):]
    except Exception:
        pass

    storage.add_message(
        session_id=session_id,
        user_id=user_id,
        role="bot",
        content=bot_reply,
        retrieved_memories=retrieved_memories,
        new_facts=new_facts,
        assistant_type=assistant_type
    )

    updated_session = storage.get_session(session_id, user_id=user_id)

    return {
        "reply": bot_reply,
        "retrieved_memories": retrieved_memories,
        "executed_tools": executed_tools,
        "new_facts": new_facts,
        "thread_id": session_id,
        "session": updated_session
    }


# =========================================================================
# MEMORIES ENDPOINTS (USER-ISOLATED)
# =========================================================================

@app.get("/api/memories")
async def get_memories(request: Request):
    user_id = get_current_user_id(request)
    if is_guest_user(user_id):
        return {"memories": [], "count": 0, "is_guest": True}
    try:
        coll = vector_db._collection.get(where={"user_id": user_id})
        memories = []
        if coll and "ids" in coll and coll["ids"]:
            for m_id, doc in zip(coll["ids"], coll["documents"]):
                memories.append({"id": m_id, "text": doc})
        return {"memories": memories, "count": len(memories)}
    except Exception:
        return {"memories": [], "count": 0}


@app.post("/api/memories")
async def add_memory(req: MemoryCreateRequest, request: Request):
    user_id = get_current_user_id(request)
    if is_guest_user(user_id):
        raise HTTPException(
            status_code=401,
            detail="Sign in required to store long-term memories in Vault. Please sign in or create an account."
        )
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Memory text cannot be empty")

    mem_id = str(uuid.uuid4())
    vector_db.add_texts([text], ids=[mem_id], metadatas=[{"user_id": user_id}])
    return {"status": "created", "id": mem_id, "text": text}


@app.delete("/api/memories/{memory_id}")
async def delete_memory(memory_id: str):
    try:
        vector_db._collection.delete(ids=[memory_id])
        return {"status": "deleted", "id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset")
async def reset_session(request: Request):
    user_id = get_current_user_id(request)
    new_session = storage.create_session(user_id=user_id)
    return {"status": "reset", "thread_id": new_session["id"], "session": new_session}


@app.get("/api/stats")
async def get_stats(request: Request):
    user_id = get_current_user_id(request)
    try:
        coll = vector_db._collection.get(where={"user_id": user_id})
        mem_count = len(coll["ids"]) if coll and "ids" in coll else 0
    except Exception:
        mem_count = 0
    sessions = storage.get_all_sessions(user_id)
    model_name = getattr(llm, "model_name", getattr(llm, "model", "Groq / OpenAI"))
    
    return {
        "total_sessions": len(sessions),
        "total_memories": mem_count,
        "model": model_name
    }


# Mount static directory to serve frontend assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Memory Chatbot API Running. Place index.html in static/ folder."}

from fastapi.responses import FileResponse, HTMLResponse
import booking_system.booking_db as booking_db
import booking_system.flight_service as flight_service

@app.get("/pay/{pnr}", response_class=HTMLResponse)

async def checkout_flight_payment(pnr: str):
    booking = booking_db.get_booking_by_pnr(pnr)
    if not booking:
        return HTMLResponse("<h1>❌ Invalid or Expired Booking PNR</h1>", status_code=404)

    is_paid = booking["payment_status"] == "PAID"
    status_badge = '<span style="background: #22c55e; color: white; padding: 4px 12px; border-radius: 99px; font-weight: bold;">CONFIRMED (PAID)</span>' if is_paid else '<span style="background: #f59e0b; color: white; padding: 4px 12px; border-radius: 99px; font-weight: bold;">PENDING PAYMENT</span>'

    pay_button_html = f'''
        <button id="pay-btn" onclick="processPayment()" style="width: 100%; background: #2563eb; color: white; border: none; padding: 14px; font-size: 16px; font-weight: bold; border-radius: 12px; cursor: pointer; transition: 0.2s;">
            Pay ₹{booking['price_inr']:,} via UPI / Card
        </button>
    ''' if not is_paid else '''
        <div style="background: #dcfce7; color: #15803d; border: 2px solid #22c55e; padding: 14px; border-radius: 12px; text-align: center; font-weight: bold;">
            ✅ Payment Received! Your E-Ticket Boarding Pass is Issued.
        </div>
    '''

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flight Payment Checkout - BOT-O-BRAIN</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
            .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 20px; max-width: 480px; width: 100%; padding: 28px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }}
            .header {{ text-align: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 20px; }}
            .info-row {{ display: flex; justify-content: space-between; margin: 12px 0; color: #94a3b8; font-size: 14px; }}
            .info-val {{ color: #f8fafc; font-weight: 600; }}
            .price-tag {{ font-size: 28px; font-weight: 700; color: #38bdf8; text-align: center; margin: 16px 0; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h2 style="margin: 0; color: #38bdf8;">✈️ Flight Checkout</h2>
                <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 13px;">BOT-O-BRAIN Booking System</p>
            </div>
            
            <div class="info-row"><span>PNR Code:</span><span class="info-val"><code>{booking['pnr']}</code></span></div>
            <div class="info-row"><span>Passenger:</span><span class="info-val">{booking['passenger_name']}</span></div>
            <div class="info-row"><span>Flight:</span><span class="info-val">{booking['airline']} ({booking['flight_number']})</span></div>
            <div class="info-row"><span>Route:</span><span class="info-val">{booking['origin']} ➔ {booking['destination']}</span></div>
            <div class="info-row"><span>Date & Time:</span><span class="info-val">{booking['travel_date']} @ {booking['departure_time']}</span></div>
            <div class="info-row"><span>Status:</span>{status_badge}</div>

            <div class="price-tag">₹{booking['price_inr']:,} INR</div>

            {pay_button_html}
        </div>

        <script>
            async function processPayment() {{
                const btn = document.getElementById('pay-btn');
                btn.disabled = true;
                btn.innerText = 'Processing Payment...';
                try {{
                    const res = await fetch('/api/flight/pay/{booking['pnr']}', {{ method: 'POST' }});
                    const data = await res.json();
                    if (data.status === 'PAID') {{
                        alert('✅ Payment Successful! E-Ticket Issued.');
                        window.location.reload();
                    }} else {{
                        alert('Payment failed.');
                        btn.disabled = false;
                    }}
                }} catch (e) {{
                    alert('Error processing payment.');
                    btn.disabled = false;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/flight/pay/{pnr}")
async def process_pnr_payment(pnr: str):
    updated = flight_service.complete_booking_payment(pnr, payment_method="UPI/Card")
    return {"status": updated["payment_status"], "pnr": updated["pnr"]}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
