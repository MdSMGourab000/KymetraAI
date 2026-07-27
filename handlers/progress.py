"""Progress tracking handler."""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import upsert_user, get_progress
from utils.helpers import MAIN_MENU_KEYBOARD


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    data = get_progress(user.id)
    activities = data["activities"]
    quiz_scores = data["quiz_scores"]

    if not activities:
        await update.message.reply_text(
            "📊 *Your Progress*\n\nYou haven't studied anything yet!\n\nUse /ask, /quiz, /explain, or /flashcards to get started.",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    lines = ["📊 *Your Learning Progress*\n"]

    activity_labels = {
        "qa": "❓ Q&A",
        "quiz": "🧠 Quizzes",
        "explain": "📖 Explanations",
        "flashcards": "🃏 Flashcards",
    }

    total_sessions = 0
    for subject, acts in sorted(activities.items()):
        count = sum(acts.values())
        total_sessions += count
        parts = []
        for act_key, label in activity_labels.items():
            if act_key in acts:
                parts.append(f"{label}: {acts[act_key]}")
        lines.append(f"*{subject}*")
        lines.append("  " + " • ".join(parts))

    lines.append(f"\n📈 *Total sessions:* {total_sessions}")

    if quiz_scores:
        total_correct = sum(s["correct"] for s in quiz_scores)
        total_questions = sum(s["total"] for s in quiz_scores)
        pct = int(total_correct / total_questions * 100) if total_questions else 0
        lines.append(f"🧠 *Quiz accuracy:* {total_correct}/{total_questions} ({pct}%)")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = get_progress(user_id)
    activities = data["activities"]
    quiz_scores = data["quiz_scores"]

    if not activities:
        await query.edit_message_text(
            "📊 *Your Progress*\n\nYou haven't studied anything yet!\n\nUse /ask, /quiz, /explain, or /flashcards to get started.",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    lines = ["📊 *Your Learning Progress*\n"]
    activity_labels = {
        "qa": "❓ Q&A",
        "quiz": "🧠 Quizzes",
        "explain": "📖 Explanations",
        "flashcards": "🃏 Flashcards",
    }
    total_sessions = 0
    for subject, acts in sorted(activities.items()):
        count = sum(acts.values())
        total_sessions += count
        parts = []
        for act_key, label in activity_labels.items():
            if act_key in acts:
                parts.append(f"{label}: {acts[act_key]}")
        lines.append(f"*{subject}*")
        lines.append("  " + " • ".join(parts))

    lines.append(f"\n📈 *Total sessions:* {total_sessions}")
    if quiz_scores:
        total_correct = sum(s["correct"] for s in quiz_scores)
        total_questions = sum(s["total"] for s in quiz_scores)
        pct = int(total_correct / total_questions * 100) if total_questions else 0
        lines.append(f"🧠 *Quiz accuracy:* {total_correct}/{total_questions} ({pct}%)")

    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
