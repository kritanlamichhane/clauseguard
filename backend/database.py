import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "clauseguard.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database with row_factory set to Row."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        hashed_password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Analysis history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        risk_score INTEGER NOT NULL,
        risk_label TEXT NOT NULL,
        total_clauses INTEGER NOT NULL,
        risk_breakdown TEXT NOT NULL,
        entities TEXT NOT NULL,
        summary TEXT NOT NULL,
        clauses TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # Create index for fast user history lookup
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_history_user_id ON analysis_history (user_id)
    """)

    conn.commit()
    conn.close()


# Ensure DB schema is created on module load
init_db()


# ── Database Operations ────────────────────────────────────────────────────────

def create_user(email: str, username: str, hashed_password: str) -> Optional[Dict[str, Any]]:
    """Creates a new user in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)",
            (email.lower().strip(), username.strip(), hashed_password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT id, email, username, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetches user details (including hashed password) by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetches user details (excluding password) by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, username, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_analysis_history(
    user_id: int,
    file_name: str,
    risk_score: int,
    risk_label: str,
    total_clauses: int,
    risk_breakdown: dict,
    entities: dict,
    summary: str,
    clauses: list
) -> int:
    """Saves an analysis report to the user's history and returns the history item ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO analysis_history (
            user_id, file_name, risk_score, risk_label, total_clauses,
            risk_breakdown, entities, summary, clauses
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            file_name,
            risk_score,
            risk_label,
            total_clauses,
            json.dumps(risk_breakdown),
            json.dumps(entities),
            summary,
            json.dumps(clauses)
        )
    )
    conn.commit()
    history_id = cursor.lastrowid
    conn.close()
    return history_id


def get_user_history(user_id: int) -> List[Dict[str, Any]]:
    """Fetches summary list of analysis history items for a given user, ordered newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, file_name, risk_score, risk_label, total_clauses, summary, created_at
        FROM analysis_history
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history_detail(history_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Fetches full analysis report for a specific history item belonging to a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM analysis_history WHERE id = ? AND user_id = ?
        """,
        (history_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["risk_breakdown"] = json.loads(data["risk_breakdown"])
    data["entities"] = json.loads(data["entities"])
    data["clauses"] = json.loads(data["clauses"])
    return data


def delete_history_item(history_id: int, user_id: int) -> bool:
    """Deletes a history item for a user. Returns True if a record was deleted."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM analysis_history WHERE id = ? AND user_id = ?",
        (history_id, user_id)
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
