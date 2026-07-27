"""Start and help handlers."""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import upsert_user
from utils.helpers import MAIN_MENU_KEYBOARD


WELCOME_TEXT = """👋 *Welcome to KymetraAI!*

I'm your AI-powered study assistant. I can help you with:

📚 *Subjects:* Higher Math • Physics • Chemistry • Biology • Math • English • Language Learning • Coding

🛠 *What I can do:*
• ❓ Answer any question
• 📖 Explain concepts simply
• 🧠 Generate quizzes
• 🃏 Flashcard study sessions
• 📊 Track your learning progress
• 🌐 Respond in your language

Choose an option below or just *send me any question* to get started!"""

HELP_TEXT = """📋 *KymetraAI Commands*

/start — Show this welcome menu
/ask — Ask any question (or just type it!)
/explain — Explain a concept simply
/quiz — Start a quiz on any topic
/flashcards — Study with flashcards
/progress — View your learning stats
/language — Set your preferred language
/stop — Stop current quiz or flashcard session
/help — Show this message

💡 *Tip:* You can also just type any question directly — no command needed!"""


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
