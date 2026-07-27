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
