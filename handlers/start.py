"""
Start and Help command handlers for KymetraAI.

Handles:
- /start
- /help
"""

from telegram import Update
from telegram.ext import ContextTypes

from database.db import upsert_user
from utils.helpers import MAIN_MENU_KEYBOARD


WELCOME_NEW_USER = """
👋 *Welcome to KymetraAI!*

Your AI-powered personal study assistant.

📚 *Subjects Available:*
• Higher Math
• Physics
• Chemistry
• Biology
• Mathematics
• English
• Language Learning
• Coding

🧠 *What I can help you with:*
• Solve questions step-by-step
• Explain difficult topics
• Generate practice tests
• Prepare for exams
• Improve your learning skills

🚀 Let's start your learning journey!

Choose an option below 👇
"""


WELCOME_RETURNING_USER = """
👋 *Welcome back, {name}!*

Ready to continue learning?

Your AI tutor is waiting for your questions.

Choose an option below 👇
"""


HELP_TEXT = """
❓ *KymetraAI Help*

Commands:

/start - Start the bot
/help - Show help menu

📚 You can:
• Ask academic questions
• Solve problems
• Generate quizzes
• Learn new topics

Need assistance?
Contact our support team.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command.
    Registers users and displays welcome message.
    """

    user = update.effective_user

    if not user:
        return

    # Save user information
    is_new_user = await upsert_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    # Select welcome message
    if is_new_user:
        message = WELCOME_NEW_USER
    else:
        name = user.first_name or "Student"
        message = WELCOME_RETURNING_USER.format(name=name)

    await update.message.reply_text(
        message,
        reply_markup=MAIN_MENU_KEYBOARD,
        parse_mode="Markdown"
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Handles /help command.
    """

    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown"
    )
