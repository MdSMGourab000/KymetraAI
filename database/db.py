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
