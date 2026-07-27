import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_PATH = "kymetra.db"

SUBJECTS = [
    "Higher Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Mathematics",
    "English",
    "Language Learning",
    "Coding",
]

# Gemini model to use
GEMINI_MODEL = "gemini-1.5-flash"

# System prompt base for KymetraAI
SYSTEM_PROMPT = """You are KymetraAI, a friendly and knowledgeable educational assistant.
You help students learn subjects including: Higher Mathematics, Physics, Chemistry, Biology,
Mathematics, English, Language Learning, and Coding.

Key behaviors:
- Detect and respond in the same language the user writes in (multilingual support).
- Be encouraging, clear, and pedagogically sound.
- For math/physics, use clear notation. For coding, use code blocks.
- Keep explanations age-appropriate and progressively deeper on request.
- Never refuse educational questions.
"""
