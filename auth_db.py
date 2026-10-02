"""
================================================================================
Module: auth_db.py — User Authentication & Analysis History (SQLite)
================================================================================
Shared authentication and data persistence layer used by both the Streamlit
web UI and the Tkinter desktop application.

Uses SQLite — no external database server required.

Tables:
  - users: id, name, email, password_hash, created_at
  - analysis_history: id, user_id, input_text, result, score, verdict,
                      word_count, created_at
  - reports: id, user_id, report_name, report_content, created_at
================================================================================
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data.db")


# ─────────────────────────────────────────────
# DATABASE INITIALIZATION
# ─────────────────────────────────────────────

def get_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Creates all required tables if they do not exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                input_text TEXT NOT NULL,
                text_preview TEXT NOT NULL,
                result TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                verdict TEXT DEFAULT '',
                word_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                report_name TEXT NOT NULL,
                report_content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False


# Auto-initialize on import
initialize_database()


# ─────────────────────────────────────────────
# PASSWORD HASHING
# ─────────────────────────────────────────────

def _hash_password(password: str, salt: str) -> str:
    """Hashes password with salt using SHA-256. Never stores plaintext."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────
# USER AUTHENTICATION
# ─────────────────────────────────────────────

def register_user(name: str, email: str, password: str) -> tuple:
    """
    Registers a new user.
    Returns: (success: bool, message_or_user_id)
    """
    if not name or not name.strip():
        return (False, "Name is required.")
    if not email or not email.strip():
        return (False, "Email is required.")
    if not password or len(password) < 6:
        return (False, "Password must be at least 6 characters.")
    if "@" not in email or "." not in email:
        return (False, "Please enter a valid email address.")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email.lower().strip(),))
        if cursor.fetchone():
            conn.close()
            return (False, "An account with this email already exists.")

        salt = secrets.token_hex(16)
        password_hash = _hash_password(password, salt)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO users (name, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), email.lower().strip(), password_hash, salt, created_at),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return (True, user_id)

    except Exception as e:
        return (False, f"Registration failed: {str(e)}")


def login_user(email: str, password: str) -> tuple:
    """
    Authenticates a user.
    Returns: (success: bool, user_dict_or_error_msg)
    """
    if not email or not password:
        return (False, "Email and password are required.")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, password_hash, salt, created_at FROM users WHERE email = ?",
            (email.lower().strip(),),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return (False, "No account found with this email.")

        expected_hash = _hash_password(password, row["salt"])
        if expected_hash != row["password_hash"]:
            return (False, "Incorrect password.")

        return (True, {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "created_at": row["created_at"],
        })

    except Exception as e:
        return (False, f"Login failed: {str(e)}")


def change_password(user_id: int, old_password: str, new_password: str) -> tuple:
    """Changes user password. Returns (success, message)."""
    if not new_password or len(new_password) < 6:
        return (False, "New password must be at least 6 characters.")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, salt FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return (False, "User not found.")

        if _hash_password(old_password, row["salt"]) != row["password_hash"]:
            conn.close()
            return (False, "Current password is incorrect.")

        new_salt = secrets.token_hex(16)
        new_hash = _hash_password(new_password, new_salt)
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
            (new_hash, new_salt, user_id),
        )
        conn.commit()
        conn.close()
        return (True, "Password changed successfully.")

    except Exception as e:
        return (False, f"Error: {str(e)}")


def update_user_name(user_id: int, new_name: str) -> tuple:
    """Updates user display name."""
    if not new_name or not new_name.strip():
        return (False, "Name cannot be empty.")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = ? WHERE id = ?", (new_name.strip(), user_id))
        conn.commit()
        conn.close()
        return (True, "Name updated successfully.")
    except Exception as e:
        return (False, str(e))


# ─────────────────────────────────────────────
# ANALYSIS HISTORY
# ─────────────────────────────────────────────

def save_analysis(user_id: int, input_text: str, score: int,
                  verdict: str, word_count: int) -> tuple:
    """Saves an analysis record. Returns (success, record_id_or_error)."""
    try:
        preview = input_text[:100].replace("\n", " ").strip()
        if len(input_text) > 100:
            preview += "..."
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO analysis_history
               (user_id, input_text, text_preview, result, score, verdict, word_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, input_text, preview, verdict, score, verdict, word_count, created_at),
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return (True, record_id)
    except Exception as e:
        return (False, str(e))


def get_user_history(user_id: int, limit: int = 100) -> list:
    """Returns analysis history for a specific user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, text_preview, result, score, verdict, word_count, created_at
               FROM analysis_history WHERE user_id = ?
               ORDER BY id DESC LIMIT ?""",
            (user_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []


def delete_analysis(user_id: int, record_id: int) -> tuple:
    """Deletes a specific analysis record."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM analysis_history WHERE id = ? AND user_id = ?",
            (record_id, user_id),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        if affected > 0:
            return (True, "Record deleted.")
        return (False, "Record not found.")
    except Exception as e:
        return (False, str(e))


def clear_user_history(user_id: int) -> tuple:
    """Deletes all analysis records for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_history WHERE user_id = ?", (user_id,))
        conn.commit()
        count = cursor.rowcount
        conn.close()
        return (True, f"Cleared {count} record(s).")
    except Exception as e:
        return (False, str(e))


def get_user_stats(user_id: int) -> dict:
    """Returns aggregate statistics for the dashboard."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM analysis_history WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM analysis_history WHERE user_id = ? AND score > 65",
            (user_id,),
        )
        suspicious = cursor.fetchone()["c"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM analysis_history WHERE user_id = ? AND score <= 35",
            (user_id,),
        )
        reliable = cursor.fetchone()["c"]

        needs_verify = total - suspicious - reliable

        cursor.execute(
            "SELECT COALESCE(SUM(word_count), 0) as total_words FROM analysis_history WHERE user_id = ?",
            (user_id,),
        )
        total_words = cursor.fetchone()["total_words"]

        cursor.execute(
            "SELECT COUNT(*) as c FROM reports WHERE user_id = ?", (user_id,),
        )
        reports_count = cursor.fetchone()["c"]

        conn.close()

        return {
            "total_analyses": total,
            "suspicious": suspicious,
            "reliable": reliable,
            "needs_verification": needs_verify,
            "total_words": total_words,
            "reports_generated": reports_count,
        }
    except Exception:
        return {
            "total_analyses": 0, "suspicious": 0, "reliable": 0,
            "needs_verification": 0, "total_words": 0, "reports_generated": 0,
        }


# ─────────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────────

def save_report(user_id: int, report_name: str, report_content: str) -> tuple:
    """Saves a generated report."""
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reports (user_id, report_name, report_content, created_at) VALUES (?, ?, ?, ?)",
            (user_id, report_name, report_content, created_at),
        )
        conn.commit()
        rid = cursor.lastrowid
        conn.close()
        return (True, rid)
    except Exception as e:
        return (False, str(e))


def get_user_reports(user_id: int) -> list:
    """Returns all reports for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, report_name, created_at FROM reports WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []


def get_report_content(user_id: int, report_id: int) -> tuple:
    """Returns a specific report content."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT report_content FROM reports WHERE id = ? AND user_id = ?",
            (report_id, user_id),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return (True, row["report_content"])
        return (False, "Report not found.")
    except Exception as e:
        return (False, str(e))
