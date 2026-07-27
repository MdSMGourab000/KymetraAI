from database.db import get_connection


def user_exists(user_id: int) -> bool:
    """Check if a user exists."""

    conn = get_connection()

    row = conn.execute(
        "SELECT 1 FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    return row is not None


def get_user(user_id: int):
    """Return a user's information."""

    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    return row


def create_user(
    user_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None = None,
):
    """Create a new user."""

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO users (
            user_id,
            username,
            first_name,
            last_name
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            username,
            first_name,
            last_name,
        ),
    )

    conn.commit()
    conn.close()


def update_user(
    user_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None,
):
    """Update user information."""

    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET
            username = ?,
            first_name = ?,
            last_name = ?,
            last_active = datetime('now')
        WHERE user_id = ?
        """,
        (
            username,
            first_name,
            last_name,
            user_id,
        ),
    )

    conn.commit()
    conn.close()


def upsert_user(
    user_id: int,
    username: str | None,
    first_name: str,
    last_name: str | None = None,
) -> bool:
    """
    Insert or update a user.

    Returns:
        True = New user
        False = Existing user
    """

    if user_exists(user_id):

        update_user(
            user_id,
            username,
            first_name,
            last_name,
        )

        return False

    create_user(
        user_id,
        username,
        first_name,
        last_name,
    )

    return True


def delete_user(user_id: int):
    """Delete a user."""

    conn = get_connection()

    conn.execute(
        "DELETE FROM users WHERE user_id = ?",
        (user_id,),
    )

    conn.commit()
    conn.close()

def ban_user(user_id: int):
    """Ban a user."""

    conn = get_connection()

    conn.execute(
        "UPDATE users SET is_banned = 1 WHERE user_id = ?",
        (user_id,),
    )

    conn.commit()
    conn.close()


def unban_user(user_id: int):
    """Unban a user."""

    conn = get_connection()

    conn.execute(
        "UPDATE users SET is_banned = 0 WHERE user_id = ?",
        (user_id,),
    )

    conn.commit()
    conn.close()


def is_banned(user_id: int) -> bool:
    """Check whether a user is banned."""

    conn = get_connection()

    row = conn.execute(
        "SELECT is_banned FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    return bool(row["is_banned"]) if row else False


def set_admin(user_id: int, value: bool):
    """Grant or revoke admin permissions."""

    conn = get_connection()

    conn.execute(
        "UPDATE users SET is_admin = ? WHERE user_id = ?",
        (1 if value else 0, user_id),
    )

    conn.commit()
    conn.close()


def is_admin(user_id: int) -> bool:
    """Check whether a user is an admin."""

    conn = get_connection()

    row = conn.execute(
        "SELECT is_admin FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    return bool(row["is_admin"]) if row else False


def set_premium(user_id: int, value: bool):
    """Enable or disable premium."""

    conn = get_connection()

    conn.execute(
        "UPDATE users SET is_premium = ? WHERE user_id = ?",
        (1 if value else 0, user_id),
    )

    conn.commit()
    conn.close()


def is_premium(user_id: int) -> bool:
    """Check premium status."""

    conn = get_connection()

    row = conn.execute(
        "SELECT is_premium FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    return bool(row["is_premium"]) if row else False


def get_language(user_id: int) -> str:
    """Return the user's preferred language."""

    conn = get_connection()

    row = conn.execute(
        "SELECT language FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    return row["language"] if row else "auto"


def set_language(user_id: int, language: str):
    """Update the user's language."""

    conn = get_connection()

    conn.execute(
        "UPDATE users SET language = ? WHERE user_id = ?",
        (language, user_id),
    )

    conn.commit()
    conn.close()


def get_timezone(user_id: int) -> str:
    """Return the user's timezone."""

    conn = get_connection()

    row = conn.execute(
        "SELECT timezone FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    return row["timezone"] if row else "UTC"


def set_timezone(user_id: int, timezone: str):
    """Update the user's timezone."""

    conn = get_connection()

    conn.execute(
        "UPDATE users SET timezone = ? WHERE user_id = ?",
        (timezone, user_id),
    )

    conn.commit()
    conn.close()
