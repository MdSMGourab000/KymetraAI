"""Flashcard study session handler."""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import (
    upsert_user, get_user_language, record_activity,
    save_flashcard_session, get_flashcard_session,
    flip_flashcard, next_flashcard, delete_flashcard_session,
)
from services.gemini_service import generate_flashcards, detect_subject
from utils.helpers import build_flashcard_keyboard, MAIN_MENU_KEYBOARD


async def flashcards_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)

    topic = " ".join(context.args) if context.args else None
    if not topic:
        await update.message.reply_text(
            "🃏 *Flashcard Mode*\n\nUsage: `/flashcards <topic>`\n\nExamples:\n• `/flashcards JavaScript array methods`\n• `/flashcards French irregular verbs`\n• `/flashcards chemical elements`",
            parse_mode="Markdown",
        )
        return

    await _start_flashcards(update, context, user.id, topic)


async def flashcards_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles 'Flashcards' menu button — asks for topic."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🃏 *Flashcard Mode*\n\nSend me a topic for flashcards!\n\nExample: `French verbs`, `Python syntax`, `organic chemistry`",
        parse_mode="Markdown",
    )
    context.user_data["awaiting"] = "flashcard_topic"


async def _start_flashcards(update, context, user_id: int, topic: str):
    msg = await update.message.reply_text("⏳ Creating flashcards…")

    try:
        lang = get_user_language(user_id)
        cards = generate_flashcards(topic, num_cards=8, user_lang=lang)
        save_flashcard_session(user_id, topic, cards)
        subject = detect_subject(topic)
        record_activity(user_id, subject, "flashcards")

        await msg.edit_text(
            f"🃏 *Flashcards: {topic}*\n_{len(cards)} cards — tap 'Reveal answer' to flip!_",
            parse_mode="Markdown",
        )
        await _send_card(msg, user_id, send_new=True, original_msg=msg)
    except Exception as e:
        await msg.edit_text(
            f"⚠️ Couldn't create flashcards. Try a different topic.\n\n_Error: {e}_",
            parse_mode="Markdown",
        )


async def _send_card(message_obj, user_id: int, send_new: bool = False, original_msg=None):
    session = get_flashcard_session(user_id)
    if not session:
        await message_obj.edit_text("❌ No active flashcard session. Use /flashcards to start.")
        return

    cards = session["cards"]
    idx = session["current_index"]
    total = len(cards)
    show_back = session["show_back"]

    if idx >= total:
        delete_flashcard_session(user_id)
        await message_obj.reply_text(
            f"🎉 *You've completed all {total} flashcards!*\n\nGreat study session!",
            parse_mode="Markdown",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    card = cards[idx]
    is_last = idx == total - 1

    if not show_back:
        text = (
            f"🃏 *Card {idx + 1}/{total}*\n\n"
            f"*Front:*\n{card['front']}"
        )
    else:
        text = (
            f"🃏 *Card {idx + 1}/{total}*\n\n"
            f"*Front:*\n{card['front']}\n\n"
            f"*Back:*\n{card['back']}"
        )

    kb = build_flashcard_keyboard(show_back, is_last)

    if send_new:
        await original_msg.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await message_obj.edit_text(text, parse_mode="Markdown", reply_markup=kb)


async def flashcard_flip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    flip_flashcard(user_id)
    await _send_card(query.message, user_id)


async def flashcard_next_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    next_flashcard(user_id)
    await _send_card(query.message, user_id)


async def flashcard_stop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    delete_flashcard_session(query.from_user.id)
    await query.edit_message_text(
        "Flashcard session ended. Use /flashcards to start a new one.",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
