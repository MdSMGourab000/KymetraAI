"""Language preference handler."""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import upsert_user, set_user_language, get_user_language
from utils.helpers import LANGUAGE_KEYBOARD, MAIN_MENU_KEYBOARD


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    current = get_user_language(user.id)
    label = "Auto-detect" if current == "auto" else current

    await update.message.reply_text(
        f"🌐 *Language Settings*\n\nCurrent: *{label}*\n\nChoose your preferred response language:",
        parse_mode="Markdown",
        reply_markup=LANGUAGE_KEYBOARD,
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = query.data.replace("lang_", "")
    set_user_language(query.from_user.id, lang_code)

    label = "Auto-detect" if lang_code == "auto" else lang_code
    await query.edit_message_text(
        f"🌐 Language set to *{label}*!\n\nI'll respond in {label} from now on.",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def language_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    current = get_user_language(user_id)
    label = "Auto-detect" if current == "auto" else current

    await query.edit_message_text(
        f"🌐 *Language Settings*\n\nCurrent: *{label}*\n\nChoose your preferred response language:",
        parse_mode="Markdown",
        reply_markup=LANGUAGE_KEYBOARD,
    )
