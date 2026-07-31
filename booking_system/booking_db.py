"""
booking_db.py — SQLite Storage for Flight Bookings
=================================================
Dedicated database management for flight reservations, PNR tracking, and payment statuses.
"""

import os
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "flight_bookings.db")

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_booking_db():
    """Initialize flight_bookings SQLite table."""
    with get_connection() as conn:
        cursor = conn.cursor()
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
                arrival_time TEXT NOT NULL,
                passenger_name TEXT NOT NULL,
                price_inr INTEGER NOT NULL,
                payment_status TEXT NOT NULL DEFAULT 'PENDING_PAYMENT',
                payment_url TEXT,
                created_at TEXT NOT NULL
            );
        """)
        conn.commit()

# Ensure table exists upon module import
init_booking_db()

def save_booking(booking_data: Dict[str, Any]) -> bool:
    """Inserts a new flight booking record into SQLite database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO flight_bookings (
                    id, pnr, user_id, origin, destination, travel_date,
                    flight_number, airline, departure_time, arrival_time,
                    passenger_name, price_inr, payment_status, payment_url, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_data["id"],
                booking_data["pnr"],
                booking_data.get("user_id", "usr_guest"),
                booking_data["origin"],
                booking_data["destination"],
                booking_data["travel_date"],
                booking_data["flight_number"],
                booking_data["airline"],
                booking_data["departure_time"],
                booking_data["arrival_time"],
                booking_data["passenger_name"],
                booking_data["price_inr"],
                booking_data.get("payment_status", "PENDING_PAYMENT"),
                booking_data.get("payment_url", ""),
                booking_data.get("created_at", datetime.now(timezone.utc).isoformat())
            ))
            conn.commit()
            return True
    except Exception as err:
        print(f"[ERROR] Failed to save booking to DB: {err}")
        return False

def get_booking_by_pnr(pnr: str) -> Optional[Dict[str, Any]]:
    """Fetches flight booking by PNR code."""
    pnr_clean = pnr.strip().upper()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flight_bookings WHERE pnr = ? OR id = ?", (pnr_clean, pnr_clean))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None

def update_payment_status(pnr: str, new_status: str = "PAID") -> Optional[Dict[str, Any]]:
    """Updates the payment status of a booking."""
    pnr_clean = pnr.strip().upper()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE flight_bookings 
            SET payment_status = ? 
            WHERE pnr = ? OR id = ?
        """, (new_status, pnr_clean, pnr_clean))
        conn.commit()
    return get_booking_by_pnr(pnr_clean)

def get_user_bookings(user_id: str = "usr_guest") -> List[Dict[str, Any]]:
    """Gets all flight bookings for a user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flight_bookings WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
