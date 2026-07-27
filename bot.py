"""KymetraAI — AI-powered Education Telegram Bot."""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from database.db import init_db

from handlers.start import start_command, help_command
from handlers.qa import ask_command, handle_free_text
from handlers.explain import explain_command
from handlers.quiz import (
    quiz_command, stop_command,
    quiz_answer_callback, quiz_stop_callback, quiz_start_callback,
)
from handlers.flashcards import (
    flashcards_command,
    flashcards_start_callback,
    flashcard_flip_callback,
    flashcard_next_callback,
    flashcard_stop_callback,
)
from handlers.progress import progress_command, progress_callback
from handlers.language import language_command, language_callback, language_menu_callback

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Check your environment secrets.")

    # Initialise database
    init_db()
    logger.info("Database initialised.")

    # Build application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ── Command handlers ───────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("explain", explain_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("flashcards", flashcards_command))
    app.add_handler(CommandHandler("progress", progress_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("stop", stop_command))

    # ── Callback query handlers ────────────────────────────────────────────────

    # Main menu buttons
    app.add_handler(CallbackQueryHandler(handle_menu_qa, pattern="^menu_qa$"))
    app.add_handler(CallbackQueryHandler(handle_menu_explain, pattern="^menu_explain$"))
    app.add_handler(CallbackQueryHandler(quiz_start_callback, pattern="^menu_quiz$"))
    app.add_handler(CallbackQueryHandler(flashcards_start_callback, pattern="^menu_flashcards$"))
    app.add_handler(CallbackQueryHandler(progress_callback, pattern="^menu_progress$"))
    app.add_handler(CallbackQueryHandler(language_menu_callback, pattern="^menu_language$"))

    # Quiz callbacks
    app.add_handler(CallbackQueryHandler(quiz_answer_callback, pattern="^quiz_ans_"))
    app.add_handler(CallbackQueryHandler(quiz_stop_callback, pattern="^quiz_stop$"))

    # Flashcard callbacks
    app.add_handler(CallbackQueryHandler(flashcard_flip_callback, pattern="^fc_flip$"))
    app.add_handler(CallbackQueryHandler(flashcard_next_callback, pattern="^fc_next$"))
    app.add_handler(CallbackQueryHandler(flashcard_stop_callback, pattern="^fc_stop$"))

    # Language selection callbacks
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

    # ── Free-text handler (must be last) ───────────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_awaiting_or_qa))

    logger.info("KymetraAI is running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


# ── Helper shims for menu buttons that just prompt the user ───────────────────

async def handle_menu_qa(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "❓ *Ask me anything!*\n\nJust send your question as a message and I'll answer it.",
        parse_mode="Markdown",
    )
    context.user_data["awaiting"] = "qa"


async def handle_menu_explain(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 *Explain a concept*\n\nSend me the concept you'd like explained.",
        parse_mode="Markdown",
    )
    context.user_data["awaiting"] = "explain"


async def handle_awaiting_or_qa(update, context):
    """Route free text based on what the user was prompted for."""
    awaiting = context.user_data.pop("awaiting", None)
    text = update.message.text.strip()

    if awaiting == "quiz_topic":
        from handlers.quiz import _start_quiz
        await _start_quiz(update, context, update.effective_user.id, text, via_callback=False)
    elif awaiting == "flashcard_topic":
        from handlers.flashcards import _start_flashcards
        await _start_flashcards(update, context, update.effective_user.id, text)
    elif awaiting == "explain":
        from handlers.explain import explain_command
        context.args = text.split()
        await explain_command(update, context)
    else:
        # Default: Q&A
        await handle_free_text(update, context)


if __name__ == "__main__":
    main()
