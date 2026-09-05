"""
storage.py — SQLite Storage Module for Multi-User Chat & Secure Authentication
================================================================================
Provides persistent storage for secure user authentication, 6-digit OTP verification,
private chat sessions, thread metadata, and user-isolated message history.
"""

import os
import json
import sqlite3
import uuid
import random
import hashlib
import bcrypt
from datetime import datetime, timezone, timedelta

OTP_VALIDITY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "chatbot_history.db")
SALT = "bot_o_brain_secure_salt_2026"  # legacy-hash pepper, kept only to verify pre-bcrypt accounts

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """bcrypt with a per-password random salt (replaces the old flat SHA-256 + static salt)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _legacy_hash_password(password: str) -> str:
    return hashlib.sha256(f"{password}{SALT}".encode('utf-8')).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies against bcrypt hashes; falls back to the legacy SHA-256 scheme
    for accounts created before the bcrypt migration."""
    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        except ValueError:
            return False
    return stored_hash == _legacy_hash_password(password)

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        # Table for Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL DEFAULT 'User',
                email TEXT UNIQUE,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                otp_code TEXT,
                otp_expires_at TEXT,
                created_at TEXT NOT NULL
            );
        """)
        # Table for Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'usr_guest',
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        # Table for Messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL DEFAULT 'usr_guest',
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                retrieved_memories TEXT,
                new_facts TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # Table for Flight Bookings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flight_bookings (
                id TEXT PRIMARY KEY,
                pnr TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL DEFAULT 'usr_guest',
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                travel_date TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                airline TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                passenger_name TEXT NOT NULL,
                price_inr INTEGER NOT NULL,
                payment_status TEXT NOT NULL DEFAULT 'PENDING_PAYMENT',
                payment_url TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        
        # Migrations for existing DBs
        migrations = [
            "ALTER TABLE users ADD COLUMN full_name TEXT NOT NULL DEFAULT 'User'",
            "ALTER TABLE users ADD COLUMN email TEXT",
            "ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 1",
            "ALTER TABLE users ADD COLUMN otp_code TEXT",
            "ALTER TABLE users ADD COLUMN otp_expires_at TEXT",
            "ALTER TABLE sessions ADD COLUMN user_id TEXT DEFAULT 'usr_guest'",
            "ALTER TABLE messages ADD COLUMN user_id TEXT DEFAULT 'usr_guest'",
            "ALTER TABLE sessions ADD COLUMN assistant_type TEXT DEFAULT 'general'",
            "ALTER TABLE users ADD COLUMN otp_attempts INTEGER DEFAULT 0",
        ]
        for m in migrations:
            try:
                cursor.execute(m)
            except Exception:
                pass
        conn.commit()

init_db()

def get_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()

# =========================================================================
# SECURE USER AUTHENTICATION & OTP
# =========================================================================

def register_user(full_name: str, email: str, username: str, password: str) -> dict:
    full_name = full_name.strip()
    email = email.strip().lower()
    username = username.strip().lower()

    if not full_name:
        raise ValueError("Full Name is required.")
    if not email or "@" not in email or "." not in email:
        raise ValueError("Please enter a valid Email address.")
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    pwd_hash = hash_password(password)
    user_id = f"usr_{str(uuid.uuid4())[:8]}"
    otp_code = generate_otp()
    now = get_iso_now()
    otp_expires_at = (datetime.now(timezone.utc) + timedelta(minutes=OTP_VALIDITY_MINUTES)).isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise ValueError("Username is already registered. Please choose another.")

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            raise ValueError("Email address is already registered. Please log in.")

        cursor.execute(
            """INSERT INTO users
               (id, full_name, email, username, password_hash, is_verified, otp_code, otp_expires_at, otp_attempts, created_at)
               VALUES (?, ?, ?, ?, ?, 0, ?, ?, 0, ?)""",
            (user_id, full_name, email, username, pwd_hash, otp_code, otp_expires_at, now)
        )
        conn.commit()

    return {
        "id": user_id,
        "full_name": full_name,
        "email": email,
        "username": username,
        "is_verified": False,
        "otp_demo": otp_code,
        "created_at": now
    }

def verify_email_otp(email: str, otp_code: str) -> dict:
    email = email.strip().lower()
    otp_code = otp_code.strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, full_name, email, username, is_verified, otp_code, otp_expires_at, otp_attempts, created_at FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        if not user:
            raise ValueError("User not found for this email address.")

        if user["is_verified"] == 1:
            return dict(user)

        attempts = user["otp_attempts"] or 0
        if attempts >= OTP_MAX_ATTEMPTS:
            raise ValueError("Too many incorrect attempts. Please request a new OTP code.")

        expires_at = user["otp_expires_at"]
        if expires_at and datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
            raise ValueError("This OTP code has expired. Please request a new one.")

        if user["otp_code"] != otp_code:
            cursor.execute("UPDATE users SET otp_attempts = ? WHERE email = ?", (attempts + 1, email))
            conn.commit()
            raise ValueError("Invalid 6-digit OTP code. Please check and try again.")

        cursor.execute(
            "UPDATE users SET is_verified = 1, otp_code = NULL, otp_attempts = 0 WHERE email = ?",
            (email,)
        )
        conn.commit()

        cursor.execute(
            "SELECT id, full_name, email, username, is_verified, created_at FROM users WHERE email = ?",
            (email,)
        )
        return dict(cursor.fetchone())

def resend_otp(email: str) -> str:
    email = email.strip().lower()
    new_otp = generate_otp()
    new_expires_at = (datetime.now(timezone.utc) + timedelta(minutes=OTP_VALIDITY_MINUTES)).isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, is_verified FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user:
            raise ValueError("User not found for this email address.")
        if user["is_verified"] == 1:
            raise ValueError("Account is already verified.")

        cursor.execute(
            "UPDATE users SET otp_code = ?, otp_expires_at = ?, otp_attempts = 0 WHERE email = ?",
            (new_otp, new_expires_at, email)
        )
        conn.commit()

    return new_otp

def login_user(login_identifier: str, password: str) -> dict:
    identifier = login_identifier.strip().lower()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, full_name, email, username, is_verified, created_at, password_hash
               FROM users
               WHERE (email = ? OR username = ?)""",
            (identifier, identifier)
        )
        user = cursor.fetchone()
        if not user or not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email/username or password.")

        if user["is_verified"] == 0:
            raise ValueError("Email not verified yet! Please enter the 6-digit OTP code sent to your email.")

        # Transparently upgrade pre-bcrypt accounts on next successful login.
        if not user["password_hash"].startswith(("$2a$", "$2b$", "$2y$")):
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hash_password(password), user["id"])
            )
            conn.commit()

        result = dict(user)
        result.pop("password_hash", None)
        return result

def get_user_by_id(user_id: str) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, username, is_verified, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

# =========================================================================
# SESSIONS & MESSAGES (USER-SCOPED)
# =========================================================================

def get_all_sessions(user_id: str, assistant_type: str = None) -> list:
    with get_connection() as conn:
        cursor = conn.cursor()
        if assistant_type:
            cursor.execute("""
                SELECT s.id, s.user_id, s.title, s.created_at, s.updated_at, s.assistant_type, COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                WHERE s.user_id = ? AND s.assistant_type = ?
                GROUP BY s.id
                ORDER BY s.updated_at DESC
            """, (user_id, assistant_type))
        else:
            cursor.execute("""
                SELECT s.id, s.user_id, s.title, s.created_at, s.updated_at, s.assistant_type, COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                WHERE s.user_id = ?
                GROUP BY s.id
                ORDER BY s.updated_at DESC
            """, (user_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def create_session(user_id: str, session_id: str = None, title: str = "New Chat", assistant_type: str = "general") -> dict:
    if not session_id:
        session_id = f"session-{str(uuid.uuid4())[:8]}"
    now = get_iso_now()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, user_id, title, created_at, updated_at, assistant_type) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, user_id, title, now, now, assistant_type)
        )
        conn.commit()
    return {"id": session_id, "user_id": user_id, "title": title, "created_at": now, "updated_at": now, "assistant_type": assistant_type, "message_count": 0}

def get_session(session_id: str, user_id: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        else:
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_session_title(session_id: str, title: str, user_id: str = None):
    now = get_iso_now()
    with get_connection() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                (title, now, session_id, user_id)
            )
        else:
            cursor.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, session_id)
            )
        conn.commit()

def delete_session(session_id: str, user_id: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("DELETE FROM messages WHERE session_id = ? AND user_id = ?", (session_id, user_id))
            cursor.execute("DELETE FROM sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        else:
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()

def add_message(session_id: str, user_id: str, role: str, content: str, retrieved_memories: list = None, new_facts: list = None, assistant_type: str = "general") -> dict:
    msg_id = str(uuid.uuid4())
    now = get_iso_now()
    memories_json = json.dumps(retrieved_memories or [])
    facts_json = json.dumps(new_facts or [])

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        session_row = cursor.fetchone()
        if not session_row:
            cursor.execute(
                "INSERT INTO sessions (id, user_id, title, created_at, updated_at, assistant_type) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, user_id, "New Chat", now, now, assistant_type)
            )
            session_title = "New Chat"
        else:
            session_title = session_row["title"]

        cursor.execute(
            "INSERT INTO messages (id, session_id, user_id, role, content, retrieved_memories, new_facts, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (msg_id, session_id, user_id, role, content, memories_json, facts_json, now)
        )
        cursor.execute("UPDATE sessions SET updated_at = ? WHERE id = ? AND user_id = ?", (now, session_id, user_id))
        
        # Auto-title session based on first user message if title is default
        if role == "user" and session_title == "New Chat":
            clean_title = content.strip().replace("\n", " ")
            if len(clean_title) > 32:
                clean_title = clean_title[:32] + "..."
            if clean_title:
                cursor.execute("UPDATE sessions SET title = ? WHERE id = ? AND user_id = ?", (clean_title, session_id, user_id))

        conn.commit()
        
    return {
        "id": msg_id,
        "session_id": session_id,
        "user_id": user_id,
        "role": role,
        "content": content,
        "retrieved_memories": retrieved_memories or [],
        "new_facts": new_facts or [],
        "timestamp": now
    }

def get_session_messages(session_id: str, user_id: str = None) -> list:
    with get_connection() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute(
                "SELECT * FROM messages WHERE session_id = ? AND user_id = ? ORDER BY timestamp ASC",
                (session_id, user_id)
            )
        else:
            cursor.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
        rows = cursor.fetchall()
        messages = []
        for r in rows:
            m = dict(r)
            m["retrieved_memories"] = json.loads(m["retrieved_memories"]) if m["retrieved_memories"] else []
            m["new_facts"] = json.loads(m["new_facts"]) if m["new_facts"] else []
            messages.append(m)
        return messages
