"""Shared helpers for handlers."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


MAIN_MENU_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("❓ Ask a question", callback_data="menu_qa"),
        InlineKeyboardButton("📖 Explain concept", callback_data="menu_explain"),
    ],
    [
        InlineKeyboardButton("🧠 Quiz me", callback_data="menu_quiz"),
        InlineKeyboardButton("🃏 Flashcards", callback_data="menu_flashcards"),
    ],
    [
        InlineKeyboardButton("📊 My progress", callback_data="menu_progress"),
        InlineKeyboardButton("🌐 Set language", callback_data="menu_language"),
    ],
])


def build_quiz_options_keyboard(options: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(options[:4]):
        buttons.append([InlineKeyboardButton(opt, callback_data=f"quiz_ans_{letters[i]}")])
    buttons.append([InlineKeyboardButton("❌ Stop quiz", callback_data="quiz_stop")])
    return InlineKeyboardMarkup(buttons)


def build_flashcard_keyboard(show_back: bool, is_last: bool) -> InlineKeyboardMarkup:
    if not show_back:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👁 Reveal answer", callback_data="fc_flip")],
            [InlineKeyboardButton("❌ Stop", callback_data="fc_stop")],
        ])
    else:
        row = []
        if not is_last:
            row.append(InlineKeyboardButton("➡️ Next card", callback_data="fc_next"))
        row.append(InlineKeyboardButton("❌ Stop", callback_data="fc_stop"))
        return InlineKeyboardMarkup([row])


def escape_md(text: str) -> str:
    """Escape MarkdownV2 special characters."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


LANGUAGE_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_English"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_Russian"),
    ],
    [
        InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_German"),
        InlineKeyboardButton("🇫🇷 Français", callback_data="lang_French"),
    ],
    [
        InlineKeyboardButton("🇪🇸 Español", callback_data="lang_Spanish"),
        InlineKeyboardButton("🇨🇳 中文", callback_data="lang_Chinese"),
    ],
    [
        InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_Arabic"),
        InlineKeyboardButton("🇯🇵 日本語", callback_data="lang_Japanese"),
    ],
    [
        InlineKeyboardButton("🔄 Auto-detect", callback_data="lang_auto"),
    ],
])
