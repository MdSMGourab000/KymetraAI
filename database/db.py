import sqlite3
from config import DATABASE_PATH


def get_connection():
    """
    Create and return a SQLite connection.
    """

    conn = sqlite3.connect(DATABASE_PATH)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


from datetime import datetime

def initialize_statistics(user_id: int):
    """
    Create a statistics record for a user if one doesn't already exist.
    """

    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO user_statistics (user_id)
        VALUES (?)
        """,
        (user_id,),
    )

    conn.commit()
    conn.close()


def add_xp(user_id: int, xp: int):
    """
    Add XP to a user and automatically update their level.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Get current total XP
    cursor.execute(
        """
        SELECT total_xp
        FROM user_statistics
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return

    new_total_xp = row["total_xp"] + xp
    new_level = (new_total_xp // 100) + 1

    cursor.execute(
        """
        UPDATE user_statistics
        SET
            xp = xp + ?,
            total_xp = ?,
            level = ?,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (
            xp,
            new_total_xp,
            new_level,
            user_id,
        ),
    )

    conn.commit()
    conn.close()


from datetime import datetime, timedelta


def update_streak(user_id: int):
    """
    Update the user's daily study streak.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT current_streak,
               longest_streak,
               last_study_date
        FROM user_statistics
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return

    today = datetime.utcnow().date()

    if row["last_study_date"]:
        last_date = datetime.fromisoformat(row["last_study_date"]).date()
    else:
        last_date = None

    current_streak = row["current_streak"]
    longest_streak = row["longest_streak"]

    if last_date == today:
        # Already studied today
        conn.close()
        return

    elif last_date == today - timedelta(days=1):
        # Consecutive day
        current_streak += 1

    else:
        # First day or streak broken
        current_streak = 1

    longest_streak = max(longest_streak, current_streak)

    cursor.execute(
        """
        UPDATE user_statistics
        SET
            current_streak = ?,
            longest_streak = ?,
            last_study_date = ?,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (
            current_streak,
            longest_streak,
            today.isoformat(),
            user_id,
        ),
    )

    conn.commit()
    conn.close()


def record_question(user_id: int):
    """
    Record that the user asked one study question.
    """

    conn = get_connection()

    conn.execute(
        """
        UPDATE user_statistics
        SET
            questions_asked = questions_asked + 1,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (user_id,),
    )

    conn.commit()
    conn.close()


def record_quiz_result(
    user_id: int,
    correct_answers: int,
    total_questions: int,
):
    """
    Record one completed quiz and update the user's quiz statistics.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            quizzes_completed,
            average_quiz_score,
            correct_answers,
            wrong_answers
        FROM user_statistics
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return

    quizzes_completed = row["quizzes_completed"] + 1

    percentage = (correct_answers / total_questions) * 100

    new_average = (
        (
            row["average_quiz_score"]
            * row["quizzes_completed"]
        )
        + percentage
    ) / quizzes_completed

    wrong_answers = total_questions - correct_answers

    cursor.execute(
        """
        UPDATE user_statistics
        SET
            quizzes_completed = ?,
            average_quiz_score = ?,
            correct_answers = correct_answers + ?,
            wrong_answers = wrong_answers + ?,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (
            quizzes_completed,
            new_average,
            correct_answers,
            wrong_answers,
            user_id,
        ),
    )

    conn.commit()
    conn.close()


def record_flashcard_completion(user_id: int):
    """
    Record one completed flashcard.
    """

    conn = get_connection()

    conn.execute(
        """
        UPDATE user_statistics
        SET
            flashcards_completed = flashcards_completed + 1,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (user_id,),
    )

    conn.commit()
    conn.close()


def record_study_session(user_id: int):
    """
    Record one completed study session.
    """

    conn = get_connection()

    conn.execute(
        """
        UPDATE user_statistics
        SET
            study_sessions = study_sessions + 1,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (user_id,),
    )

    conn.commit()
    conn.close()


def update_study_time(user_id: int, minutes: int):
    """
    Add study time (in minutes) to the user's total.
    """

    conn = get_connection()

    conn.execute(
        """
        UPDATE user_statistics
        SET
            total_study_time = total_study_time + ?,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (minutes, user_id),
    )

    conn.commit()
    conn.close()


def get_user_statistics(user_id: int):
    """
    Return all statistics for a user.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM user_statistics
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()

    conn.close()

    return row


def get_user_progress(user_id: int):
    """
    Return the user's learning progress.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            level,
            xp,
            total_xp,
            current_streak,
            longest_streak,
            questions_asked,
            quizzes_completed,
            flashcards_completed,
            study_sessions,
            correct_answers,
            wrong_answers,
            total_study_time,
            average_quiz_score
        FROM user_statistics
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()

    conn.close()

    return row


def get_leaderboard(limit: int = 10):
    """
    Return the top users ranked by total XP.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            u.user_id,
            u.full_name,
            u.username,
            s.level,
            s.total_xp,
            s.current_streak
        FROM users AS u
        INNER JOIN user_statistics AS s
            ON u.user_id = s.user_id
        ORDER BY
            s.total_xp DESC,
            s.level DESC,
            s.current_streak DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def unlock_achievement(user_id: int, achievement: str):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO achievements (user_id, achievement)
        VALUES (?, ?)
        """,
        (user_id, achievement),
    )

    conn.commit()
    conn.close()


def has_achievement(user_id: int, achievement: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM achievements
        WHERE user_id = ?
        AND achievement = ?
        """,
        (user_id, achievement),
    )

    row = cursor.fetchone()

    conn.close()

    return row is not None


def get_achievements(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT achievement, unlocked_at
        FROM achievements
        WHERE user_id = ?
        ORDER BY unlocked_at DESC
        """,
        (user_id,),
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def check_achievements(user_id: int):
    """
    Check and unlock achievements based on the user's statistics.
    """

    stats = get_user_statistics(user_id)

    if stats is None:
        return

    # First Question
    if stats["questions_asked"] >= 1:
        unlock_achievement(user_id, "🎉 First Question")

    # First Quiz
    if stats["quizzes_completed"] >= 1:
        unlock_achievement(user_id, "🧠 First Quiz")

    # First Flashcard Session
    if stats["flashcards_completed"] >= 1:
        unlock_achievement(user_id, "🃏 Flashcard Beginner")

    # Level 5
    if stats["level"] >= 5:
        unlock_achievement(user_id, "⭐ Level 5")

    # 7-Day Streak
    if stats["current_streak"] >= 7:
        unlock_achievement(user_id, "🔥 7-Day Streak")

    # 100 Questions
    if stats["questions_asked"] >= 100:
        unlock_achievement(user_id, "🏆 100 Questions")


def init_db():
    """
    Create all database tables.
    """

    conn = get_connection()

    cursor = conn.cursor()

    cursor.executescript("""

    CREATE TABLE IF NOT EXISTS users (

        user_id INTEGER PRIMARY KEY,

        username TEXT,

        first_name TEXT NOT NULL,

        last_name TEXT,

        language TEXT DEFAULT 'auto',

        timezone TEXT DEFAULT 'UTC',

        country TEXT,

        is_admin INTEGER DEFAULT 0,

        is_banned INTEGER DEFAULT 0,

        is_premium INTEGER DEFAULT 0,

        joined_at TEXT DEFAULT (datetime('now')),

        last_active TEXT DEFAULT (datetime('now'))

    );



    CREATE TABLE IF NOT EXISTS user_settings (

        user_id INTEGER PRIMARY KEY,

        theme TEXT DEFAULT 'light',

        notifications INTEGER DEFAULT 1,

        ai_personality TEXT DEFAULT 'teacher',

        preferred_subject TEXT,

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS study_sessions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        subject TEXT NOT NULL,

        activity TEXT NOT NULL,

        score TEXT,

        duration INTEGER DEFAULT 0,

        created_at TEXT DEFAULT (datetime('now')),

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS quiz_sessions (

        user_id INTEGER PRIMARY KEY,

        topic TEXT NOT NULL,

        questions TEXT NOT NULL,

        current_index INTEGER DEFAULT 0,

        correct INTEGER DEFAULT 0,

        created_at TEXT DEFAULT (datetime('now')),

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS flashcard_sessions (

        user_id INTEGER PRIMARY KEY,

        topic TEXT NOT NULL,

        cards TEXT NOT NULL,

        current_index INTEGER DEFAULT 0,

        show_back INTEGER DEFAULT 0,

        created_at TEXT DEFAULT (datetime('now')),

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS chat_history (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        role TEXT NOT NULL,

        message TEXT NOT NULL,

        created_at TEXT DEFAULT (datetime('now')),

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS bookmarks (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        title TEXT,

        content TEXT,

        created_at TEXT DEFAULT (datetime('now')),

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS user_statistics (
    user_id INTEGER PRIMARY KEY,

    xp INTEGER DEFAULT 0,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,

    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,

    questions_asked INTEGER DEFAULT 0,
    quizzes_completed INTEGER DEFAULT 0,
    flashcards_completed INTEGER DEFAULT 0,
    study_sessions INTEGER DEFAULT 0,

    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,

    total_study_time INTEGER DEFAULT 0,

    average_quiz_score REAL DEFAULT 0,

    last_study_date TEXT,

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);



    CREATE TABLE IF NOT EXISTS achievements (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        achievement TEXT NOT NULL,

        unlocked_at TEXT DEFAULT (datetime('now')),

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS notifications (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        title TEXT,

        body TEXT,

        is_read INTEGER DEFAULT 0,

        created_at TEXT DEFAULT (datetime('now')),

        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE

    );



    CREATE TABLE IF NOT EXISTS admin_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        admin_id INTEGER,

        action TEXT,

        target_user INTEGER,

        created_at TEXT DEFAULT (datetime('now'))

    );



    CREATE TABLE IF NOT EXISTS system_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        level TEXT,

        message TEXT,

        created_at TEXT DEFAULT (datetime('now'))

    );

    """)

    conn.commit()

    conn.close()
