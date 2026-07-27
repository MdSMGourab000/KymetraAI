from datetime import date, datetime

from database.db import get_connection


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


def get_statistics(user_id: int):
    """
    Return the user's statistics.
    """

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM user_statistics
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    return row


def get_or_create_statistics(user_id: int):
    """
    Return statistics, creating them if they don't exist.
    """

    stats = get_statistics(user_id)

    if stats is None:
        initialize_statistics(user_id)
        stats = get_statistics(user_id)

    return stats


def _update_stat(user_id: int, field: str, value):
    """
    Internal helper for updating a single statistics field.
    """

    allowed_fields = {
        "xp",
        "total_xp",
        "level",
        "current_streak",
        "longest_streak",
        "questions_asked",
        "quizzes_completed",
        "flashcards_completed",
        "study_sessions",
        "correct_answers",
        "wrong_answers",
        "total_study_time",
        "average_quiz_score",
        "last_study_date",
        "updated_at",
    }

    if field not in allowed_fields:
        raise ValueError(f"Invalid statistics field: {field}")

    conn = get_connection()

    conn.execute(
        f"""
        UPDATE user_statistics
        SET {field} = ?,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (value, user_id),
    )

    conn.commit()
    conn.close()


def get_xp(user_id: int) -> int:
    return get_or_create_statistics(user_id)["xp"]


def get_level(user_id: int) -> int:
    return get_or_create_statistics(user_id)["level"]


def calculate_level(xp: int) -> int:
    """
    Calculate a user's level from XP.
    """

    return (xp // 100) + 1


def add_xp(user_id: int, amount: int):
    """
    Add XP and update the user's level automatically.
    """

    # Ignore invalid XP values
    if amount <= 0:
        return

    stats = get_or_create_statistics(user_id)

    new_xp = stats["xp"] + amount
    total_xp = stats["total_xp"] + amount

    new_level = calculate_level(new_xp)

    conn = get_connection()

    conn.execute(
        """
        UPDATE user_statistics
        SET
            xp = ?,
            total_xp = ?,
            level = ?,
            updated_at = datetime('now')
        WHERE user_id = ?
        """,
        (
            new_xp,
            total_xp,
            new_level,
            user_id,
        ),
    )

    conn.commit()
    conn.close()
  


def record_study_session(
    user_id: int,
    subject: str,
    activity: str,
    duration: int = 0,
):
    """
    Record a study session.
    Duration is stored in seconds.
    """

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO study_sessions (
            user_id,
            subject,
            activity,
            duration
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            subject,
            activity,
            duration,
        ),
    )

    conn.commit()
    conn.close()

    increment_study_sessions(user_id)

    if duration > 0:
        add_study_time(user_id, duration)

    update_daily_streak(user_id)


def add_study_time(user_id: int, seconds: int):
    """
    Add study time to a user's statistics.
    """

    if seconds <= 0:
        return

    stats = get_or_create_statistics(user_id)

    total = stats["total_study_time"] + seconds

    _update_stat(
        user_id,
        "total_study_time",
        total,
    )


def increment_study_sessions(user_id: int):
    """
    Increase the study session count.
    """

    stats = get_or_create_statistics(user_id)

    sessions = stats["study_sessions"] + 1

    _update_stat(
        user_id,
        "study_sessions",
        sessions,
    )


def get_total_study_time(user_id: int) -> int:
    """
    Return total study time in seconds.
    """

    return get_or_create_statistics(user_id)["total_study_time"]


def get_total_sessions(user_id: int) -> int:
    """
    Return total study sessions.
    """

    stats = get_or_create_statistics(user_id)

    if stats is None:
        return 0

    return stats["study_sessions"]


def get_current_streak(user_id: int) -> int:
    """
    Return the user's current study streak.
    """

    stats = get_or_create_statistics(user_id)

    if stats is None:
        return 0

    return stats["current_streak"]


def get_longest_streak(user_id: int) -> int:
    """
    Return the user's longest study streak.
    """

    stats = get_or_create_statistics(user_id)

    if stats is None:
        return 0

    return stats["longest_streak"]


def update_daily_streak(user_id: int):
    """
    Update the user's daily study streak.
    """

    stats = get_or_create_statistics(user_id)

    today = date.today()

    last_date = stats["last_study_date"]

    if last_date:
        last_date = datetime.strptime(
            last_date,
            "%Y-%m-%d",
        ).date()

        difference = (today - last_date).days

        if difference == 0:
            return

        if difference == 1:
            streak = stats["current_streak"] + 1
        else:
            streak = 1

    else:
        streak = 1

    longest = max(
        streak,
        stats["longest_streak"],
    )

    conn = get_connection()

    conn.execute(
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
            streak,
            longest,
            today.isoformat(),
            user_id,
        ),
    )

    conn.commit()
    conn.close()


def increment_quizzes_completed(user_id: int):
    """
    Increase the completed quiz count.
    """

    stats = get_or_create_statistics(user_id)

    quizzes = stats["quizzes_completed"] + 1

    _update_stat(
        user_id,
        "quizzes_completed",
        quizzes,
    )


def record_quiz_result(
    user_id: int,
    correct: int,
    total: int,
):
    """
    Record a completed quiz and update statistics.
    """

    if total <= 0 or correct < 0 or correct > total:
        return

    stats = get_or_create_statistics(user_id)

    increment_quizzes_completed(user_id)

    correct_answers = stats["correct_answers"] + correct
    wrong_answers = stats["wrong_answers"] + (total - correct)

    _update_stat(
        user_id,
        "correct_answers",
        correct_answers,
    )

    _update_stat(
        user_id,
        "wrong_answers",
        wrong_answers,
    )

    update_average_quiz_score(user_id)

    add_xp(user_id, correct * 10)


def get_accuracy(user_id: int) -> float:
    """
    Return quiz accuracy percentage.
    """

    stats = get_or_create_statistics(user_id)

    correct = stats["correct_answers"]
    wrong = stats["wrong_answers"]

    total = correct + wrong

    if total == 0:
        return 0.0

    return round((correct / total) * 100, 2)


def update_average_quiz_score(user_id: int):
    """
    Update the user's average quiz accuracy.
    """

    accuracy = get_accuracy(user_id)

    _update_stat(
        user_id,
        "average_quiz_score",
        accuracy,
    )


def increment_questions_asked(user_id: int):
    """
    Increase the number of questions asked.
    """

    stats = get_or_create_statistics(user_id)

    total = stats["questions_asked"] + 1

    _update_stat(
        user_id,
        "questions_asked",
        total,
    )


def increment_flashcards_completed(user_id: int):
    """
    Increase the completed flashcards count.
    """

    stats = get_or_create_statistics(user_id)

    total = stats["flashcards_completed"] + 1

    _update_stat(
        user_id,
        "flashcards_completed",
        total,
    )
