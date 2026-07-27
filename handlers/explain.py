"""Explain a concept in simple terms."""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import upsert_user, get_user_language, record_activity
from services.gemini_service import explain_concept, detect_subject
from utils.helpers import MAIN_MENU_KEYBOARD


async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    concept = " ".join(context.args) if context.args else None
    if not concept:
        await update.message.reply_text(
            "📖 *Explain a concept*\n\nUsage: `/explain <concept>`\n\nExample: `/explain quantum entanglement`",
            parse_mode="Markdown",
        )
        return

    thinking_msg = await update.message.reply_text("📖 Preparing explanation…")

    try:
        lang = get_user_language(user.id)
        explanation = explain_concept(concept, lang)
        subject = detect_subject(concept)
        record_activity(user.id, subject, "explain")

        await thinking_msg.edit_text(
            f"📖 *{concept}*\n\n{explanation}",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
    except Exception as e:
        await thinking_msg.edit_text(
            f"⚠️ Couldn't generate explanation. Please try again.\n\n_Error: {e}_",
            parse_mode="Markdown",
        )
