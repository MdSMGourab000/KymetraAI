"""Quiz handler with inline keyboard answers."""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.db import (
    upsert_user,
    get_user_language,
    record_activity,
    save_quiz_session,
    get_quiz_session,
    advance_quiz,
    delete_quiz_session,
    initialize_statistics,
    record_quiz_result,
    record_study_session,
    update_streak,
    add_xp,
)
from services.gemini_service import generate_quiz, detect_subject
from utils.helpers import build_quiz_options_keyboard, MAIN_MENU_KEYBOARD


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username, user.first_name)
    initialize_statistics(user.id)

    topic = " ".join(context.args) if context.args else None
    if not topic:
        await update.message.reply_text(
            "🧠 *Quiz Mode*\n\nUsage: `/quiz <topic>`\n\nExamples:\n• `/quiz photosynthesis`\n• `/quiz Python lists`\n• `/quiz Newton's laws`",
            parse_mode="Markdown",
        )
        return

    await _start_quiz(update, context, user.id, topic, via_callback=False)


async def quiz_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'Quiz me' menu button — asks for topic."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🧠 *Quiz Mode*\n\nSend me a topic to quiz you on!\n\nExample: `photosynthesis`, `Python loops`, `Newton's laws`",
        parse_mode="Markdown",
    )
    context.user_data["awaiting"] = "quiz_topic"


async def _start_quiz(update, context, user_id: int, topic: str, via_callback: bool = False):
    send = update.callback_query.edit_message_text if via_callback else update.message.reply_text
    thinking_msg = await (update.callback_query.edit_message_text("⏳ Generating quiz…") if via_callback
                          else update.message.reply_text("⏳ Generating quiz…"))

    try:
        lang = get_user_language(user_id)
        questions = generate_quiz(topic, num_questions=5, user_lang=lang)
        save_quiz_session(user_id, topic, questions)
        await _send_question(thinking_msg, user_id, edit=True)
    except Exception as e:
        await thinking_msg.edit_text(
            f"⚠️ Couldn't generate quiz. Try a different topic.\n\n_Error: {e}_",
            parse_mode="Markdown",
        )


async def _send_question(message_obj, user_id: int, edit: bool = False):
    session = get_quiz_session(user_id)
    if not session:
        await message_obj.edit_text("❌ No active quiz. Use /quiz to start one.")
        return

    questions = session["questions"]
    idx = session["current_index"]
    total = len(questions)

    if idx >= total:
        # Quiz finished
        correct = session["correct"]
        subject = detect_subject(session["topic"])
        record_activity(user_id, subject, "quiz", {"correct": correct, "total": total})
        delete_quiz_session(user_id)

        pct = int(correct / total * 100)
        emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
        text = (
            f"{emoji} *Quiz complete!*\n\n"
            f"Topic: *{session['topic']}*\n"
            f"Score: *{correct}/{total}* ({pct}%)\n\n"
            + ("Excellent work! 🌟" if pct >= 80 else
               "Good job! Keep practising. 💪" if pct >= 60 else
               "Keep studying — you'll get there! 📖")
        )
        await message_obj.edit_text(text, parse_mode="Markdown", reply_markup=MAIN_MENU_KEYBOARD)
        return

    q = questions[idx]
    text = (
        f"🧠 *Question {idx + 1}/{total}*\n\n"
        f"{q['question']}\n\n"
        + "\n".join(q["options"])
    )
    kb = build_quiz_options_keyboard(q["options"])

    if edit:
        await message_obj.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await message_obj.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def quiz_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data  # "quiz_ans_A" etc.
    chosen = data.replace("quiz_ans_", "").upper()

    session = get_quiz_session(user_id)
    if not session:
        await query.edit_message_text("❌ Quiz session expired. Use /quiz to start a new one.")
        return

    idx = session["current_index"]
    q = session["questions"][idx]
    correct_letter = q["answer"].strip().upper()[0]
    is_correct = chosen == correct_letter

    advance_quiz(user_id, is_correct)

    feedback = (
        f"{'✅ Correct!' if is_correct else '❌ Wrong!'}\n\n"
        f"*Correct answer:* {correct_letter}\n"
        f"*Explanation:* {q.get('explanation', '')}"
    )

    await query.edit_message_text(feedback, parse_mode="Markdown")

    # Send next question as a new message
    session = get_quiz_session(user_id)
    if session and session["current_index"] < len(session["questions"]):
        next_q = session["questions"][session["current_index"]]
        total = len(session["questions"])
        text = (
            f"🧠 *Question {session['current_index'] + 1}/{total}*\n\n"
            f"{next_q['question']}\n\n"
            + "\n".join(next_q["options"])
        )
        kb = build_quiz_options_keyboard(next_q["options"])
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        # Finished
        correct = session["correct"] if session else 0
        total = len(session["questions"]) if session else 5
        topic = session["topic"] if session else "Unknown"
        subject = detect_subject(topic)
        record_activity(user_id, subject, "quiz", {"correct": correct, "total": total})

        record_quiz_result(user_id, correct, total)
        record_study_session(user_id)
        update_streak(user_id)

        xp = correct * 10
        add_xp(user_id, xp)

        delete_quiz_session(user_id)

        pct = int(correct / total * 100)
        emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚"
        text = (
            f"{emoji} *Quiz complete!*\n\n"
            f"Topic: *{topic}*\n"
            f"Score: *{correct}/{total}* ({pct}%)\n\n"
            + ("Excellent work! 🌟" if pct >= 80 else
               "Good job! Keep practising. 💪" if pct >= 60 else
               "Keep studying — you'll get there! 📖")
        )
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=MAIN_MENU_KEYBOARD)


async def quiz_stop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    delete_quiz_session(query.from_user.id)
    await query.edit_message_text(
        "Quiz stopped. Use /quiz to start a new one.",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop any active session."""
    user_id = update.effective_user.id
    from database.db import delete_flashcard_session
    delete_quiz_session(user_id)
    delete_flashcard_session(user_id)
    await update.message.reply_text(
        "✅ Any active quiz or flashcard session has been stopped.",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
