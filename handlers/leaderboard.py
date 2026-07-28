from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_leaderboard
from utils.helpers import MAIN_MENU_KEYBOARD


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaderboard = get_leaderboard()

    if not leaderboard:
        await update.message.reply_text(
            "🏆 No leaderboard data available yet.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    lines = ["🏆 *Leaderboard*\n"]

    medals = ["🥇", "🥈", "🥉"]

    for index, user in enumerate(leaderboard):
        if index < 3:
            rank = medals[index]
        else:
            rank = f"{index + 1}."

        name = (
            user["full_name"]
            or user["username"]
            or f"User {user['user_id']}"
        )

        lines.append(
            f"{rank} {name}\n"
            f"⭐ {user['total_xp']} XP | "
            f"🏅 Lv.{user['level']} | "
            f"🔥 {user['current_streak']} days"
        )

    await update.message.reply_text(
        "\n\n".join(lines),
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KEYBOARD,
    )