import sqlite3
import bcrypt
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent.parent / "edusync.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    UNIQUE NOT NULL,
                email      TEXT    UNIQUE NOT NULL,
                password   BLOB    NOT NULL,
                role       TEXT    NOT NULL DEFAULT 'student',
                created_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_courses (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                course_id  TEXT    NOT NULL,
                title      TEXT    NOT NULL,
                subject    TEXT,
                level      TEXT,
                role_type  TEXT,
                meta_json  TEXT,
                full_json  TEXT,
                saved_at   TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, course_id)
            );
        """)


# ── User operations ────────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str, role: str) -> bool:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, email, password, role, created_at) VALUES (?,?,?,?,?)",
                (username, email.lower(), hashed, role, datetime.utcnow().isoformat())
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return dict(row) if row else None


def get_user_by_email(email: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
    return dict(row) if row else None


def verify_password(plain: str, hashed) -> bool:
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(plain.encode(), hashed)


# ── Course operations ──────────────────────────────────────────────────────

def save_course(user_id: int, course_id: str, title: str, subject: str,
                level: str, role_type: str, meta: dict, full_data: dict) -> bool:
    try:
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO saved_courses
                    (user_id, course_id, title, subject, level, role_type,
                     meta_json, full_json, saved_at)
                VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(user_id, course_id) DO UPDATE SET
                    title=excluded.title, meta_json=excluded.meta_json,
                    full_json=excluded.full_json, saved_at=excluded.saved_at
            """, (user_id, course_id, title, subject, level, role_type,
                  json.dumps(meta), json.dumps(full_data),
                  datetime.utcnow().isoformat()))
        return True
    except Exception:
        return False


def get_courses(user_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM saved_courses WHERE user_id=? ORDER BY saved_at DESC",
            (user_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_course(user_id: int, course_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM saved_courses WHERE user_id=? AND course_id=?",
            (user_id, course_id)
        ).fetchone()
    return dict(row) if row else None


def delete_course(user_id: int, course_id: str) -> bool:
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM saved_courses WHERE user_id=? AND course_id=?",
            (user_id, course_id)
        )
    return True


# Initialise DB on import
init_db()
