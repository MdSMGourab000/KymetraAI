"""Question & Answer handler — works as free text or via /ask command."""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import upsert_user, get_user_language, record_activity
from services.gemini_service import answer_question, detect_subject
from utils.helpers import MAIN_MENU_KEYBOARD


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    question = " ".join(context.args) if context.args else None
    if not question:
        await update.message.reply_text(
            "❓ *Ask me anything!*\n\nUsage: `/ask <your question>`\n\nOr just type your question directly — no command needed!",
            parse_mode="Markdown",
        )
        return

    await _answer(update, user.id, question)


async def handle_free_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles plain messages not matched by any other handler."""
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    text = update.message.text.strip()
    if not text:
        return

    await _answer(update, user.id, text)


async def _answer(update: Update, user_id: int, question: str):
    thinking_msg = await update.message.reply_text("🤔 Thinking…")

    try:
        lang = get_user_language(user_id)
        answer = answer_question(question, lang)
        subject = detect_subject(question)
        record_activity(user_id, subject, "qa")

        await thinking_msg.edit_text(
            f"*Your question:* {question}\n\n{answer}",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
    except Exception as e:
        await thinking_msg.edit_text(
            f"⚠️ Sorry, I couldn't answer that right now. Please try again.\n\n_Error: {e}_",
            parse_mode="Markdown",
        )
