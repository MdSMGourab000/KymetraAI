import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            language    TEXT DEFAULT 'auto',
            joined_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS study_sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            subject     TEXT NOT NULL,
            activity    TEXT NOT NULL,   -- 'qa', 'quiz', 'explain', 'flashcards'
            score       INTEGER,         -- for quizzes: correct/total encoded as json
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL UNIQUE,
            topic           TEXT NOT NULL,
            questions       TEXT NOT NULL,  -- JSON list of {q, a, options}
            current_index   INTEGER DEFAULT 0,
            correct         INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS flashcard_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL UNIQUE,
            topic           TEXT NOT NULL,
            cards           TEXT NOT NULL,  -- JSON list of {front, back}
            current_index   INTEGER DEFAULT 0,
            show_back       INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()


# ── User helpers ──────────────────────────────────────────────────────────────

def upsert_user(user_id: int, username: str | None, first_name: str | None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO users (user_id, username, first_name)
           VALUES (?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name""",
        (user_id, username, first_name),
    )
    conn.commit()
    conn.close()


def get_user_language(user_id: int) -> str:
    conn = get_connection()
    row = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row["language"] if row else "auto"


def set_user_language(user_id: int, language: str):
    conn = get_connection()
    conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
    conn.commit()
    conn.close()


# ── Progress helpers ──────────────────────────────────────────────────────────

def record_activity(user_id: int, subject: str, activity: str, score: dict | None = None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO study_sessions (user_id, subject, activity, score) VALUES (?, ?, ?, ?)",
        (user_id, subject, activity, json.dumps(score) if score else None),
    )
    conn.commit()
    conn.close()


def get_progress(user_id: int) -> dict:
    conn = get_connection()
    rows = conn.execute(
        """SELECT subject, activity, COUNT(*) as count,
                  SUM(CASE WHEN score IS NOT NULL THEN 1 ELSE 0 END) as scored
           FROM study_sessions
           WHERE user_id = ?
           GROUP BY subject, activity
           ORDER BY subject""",
        (user_id,),
    ).fetchall()

    quiz_rows = conn.execute(
        """SELECT subject, score FROM study_sessions
           WHERE user_id = ? AND activity = 'quiz' AND score IS NOT NULL""",
        (user_id,),
    ).fetchall()

    conn.close()

    activities: dict = {}
    for r in rows:
        key = r["subject"]
        if key not in activities:
            activities[key] = {}
        activities[key][r["activity"]] = r["count"]

    quiz_scores = []
    for r in quiz_rows:
        try:
            s = json.loads(r["score"])
            if isinstance(s, dict) and "correct" in s and "total" in s:
                quiz_scores.append(s)
        except Exception:
            pass

    return {"activities": activities, "quiz_scores": quiz_scores}


# ── Quiz session helpers ──────────────────────────────────────────────────────

def save_quiz_session(user_id: int, topic: str, questions: list):
    conn = get_connection()
    conn.execute(
        """INSERT INTO quiz_sessions (user_id, topic, questions, current_index, correct)
           VALUES (?, ?, ?, 0, 0)
           ON CONFLICT(user_id) DO UPDATE SET
               topic=excluded.topic, questions=excluded.questions,
               current_index=0, correct=0, created_at=datetime('now')""",
        (user_id, topic, json.dumps(questions)),
    )
    conn.commit()
    conn.close()


def get_quiz_session(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM quiz_sessions WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "topic": row["topic"],
        "questions": json.loads(row["questions"]),
        "current_index": row["current_index"],
        "correct": row["correct"],
    }


def advance_quiz(user_id: int, correct: bool):
    conn = get_connection()
    conn.execute(
        """UPDATE quiz_sessions
           SET current_index = current_index + 1,
               correct = correct + ?
           WHERE user_id = ?""",
        (1 if correct else 0, user_id),
    )
    conn.commit()
    conn.close()


def delete_quiz_session(user_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM quiz_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ── Flashcard session helpers ─────────────────────────────────────────────────

def save_flashcard_session(user_id: int, topic: str, cards: list):
    conn = get_connection()
    conn.execute(
        """INSERT INTO flashcard_sessions (user_id, topic, cards, current_index, show_back)
           VALUES (?, ?, ?, 0, 0)
           ON CONFLICT(user_id) DO UPDATE SET
               topic=excluded.topic, cards=excluded.cards,
               current_index=0, show_back=0, created_at=datetime('now')""",
        (user_id, topic, json.dumps(cards)),
    )
    conn.commit()
    conn.close()


def get_flashcard_session(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM flashcard_sessions WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "topic": row["topic"],
        "cards": json.loads(row["cards"]),
        "current_index": row["current_index"],
        "show_back": bool(row["show_back"]),
    }


def flip_flashcard(user_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE flashcard_sessions SET show_back = 1 WHERE user_id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def next_flashcard(user_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE flashcard_sessions SET current_index = current_index + 1, show_back = 0 WHERE user_id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def delete_flashcard_session(user_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM flashcard_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()