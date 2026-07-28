"""Progress tracking handler."""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import (
    upsert_user,
    initialize_statistics,
    get_user_progress,
)
from utils.helpers import MAIN_MENU_KEYBOARD


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    upsert_user(user.id, user.username, user.first_name)
    initialize_statistics(user.id)

    stats = get_user_progress(user.id)

    if stats is None:
        await update.message.reply_text(
            "No statistics available yet.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    accuracy = 0
    if stats["correct_answers"] + stats["wrong_answers"] > 0:
        accuracy = (
            stats["correct_answers"] * 100
            / (stats["correct_answers"] + stats["wrong_answers"])
        )

    text = (
        "📊 *Your Progress*\n\n"
        f"🏅 Level: {stats['level']}\n"
        f"⭐ Total XP: {stats['total_xp']}\n"
        f"🔥 Current Streak: {stats['current_streak']} days\n"
        f"🏆 Longest Streak: {stats['longest_streak']} days\n\n"
        f"❓ Questions Asked: {stats['questions_asked']}\n"
        f"🧠 Quizzes Completed: {stats['quizzes_completed']}\n"
        f"🃏 Flashcards Completed: {stats['flashcards_completed']}\n"
        f"📚 Study Sessions: {stats['study_sessions']}\n\n"
        f"✅ Correct Answers: {stats['correct_answers']}\n"
        f"❌ Wrong Answers: {stats['wrong_answers']}\n"
        f"🎯 Quiz Accuracy: {accuracy:.1f}%\n"
        f"⏱️ Study Time: {stats['total_study_time']} minutes"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    initialize_statistics(user_id)

    stats = get_user_progress(user_id)

    if stats is None:
        await query.edit_message_text(
            "No statistics available yet.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    accuracy = 0
    if stats["correct_answers"] + stats["wrong_answers"] > 0:
        accuracy = (
            stats["correct_answers"] * 100
            / (stats["correct_answers"] + stats["wrong_answers"])
        )

    text = (
        "📊 *Your Progress*\n\n"
        f"🏅 Level: {stats['level']}\n"
        f"⭐ Total XP: {stats['total_xp']}\n"
        f"🔥 Current Streak: {stats['current_streak']} days\n"
        f"🏆 Longest Streak: {stats['longest_streak']} days\n\n"
        f"❓ Questions Asked: {stats['questions_asked']}\n"
        f"🧠 Quizzes Completed: {stats['quizzes_completed']}\n"
        f"🃏 Flashcards Completed: {stats['flashcards_completed']}\n"
        f"📚 Study Sessions: {stats['study_sessions']}\n\n"
        f"✅ Correct Answers: {stats['correct_answers']}\n"
        f"❌ Wrong Answers: {stats['wrong_answers']}\n"
        f"🎯 Quiz Accuracy: {accuracy:.1f}%\n"
        f"⏱️ Study Time: {stats['total_study_time']} minutes"
    )

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KEYBOARD,
    )