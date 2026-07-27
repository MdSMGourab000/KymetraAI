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
    row = get_statistics(user_id)
    return row["xp"] if row else 0


def get_level(user_id: int) -> int:
    row = get_statistics(user_id)
    return row["level"] if row else 1


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

    stats = get_statistics(user_id)

    if stats is None:
        initialize_statistics(user_id)
        stats = get_statistics(user_id)

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
  
