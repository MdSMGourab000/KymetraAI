# KymetraAI

AI-powered Education Telegram Bot built with Python, python-telegram-bot, and Google Gemini.

## Stack

- **Language:** Python 3.11+
- **Bot framework:** python-telegram-bot v21 (async)
- **AI:** Google Gemini 1.5 Flash via `google-generativeai`
- **Database:** SQLite (local file `kymetra.db`) for progress tracking
- **Dependency management:** pip / `requirements.txt`

## How to run

```
python bot.py
```

The workflow "KymetraAI Bot" runs this command automatically.

## Required secrets

| Secret | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From @BotFather on Telegram |
| `GEMINI_API_KEY` | From Google AI Studio (aistudio.google.com) |

## Features

- ❓ **Q&A** — ask any question, get an AI answer
- 🧠 **Quizzes** — generate multiple-choice practice questions on any topic
- 📖 **Explain** — explain any concept in simple terms with an analogy
- 🃏 **Flashcards** — study with flip-style flashcard sessions
- 📊 **Progress tracking** — per-user SQLite tracking of topics and quiz scores
- 🌐 **Multi-language** — auto-detect language or set a preferred language

## Subjects covered

Higher Mathematics • Physics • Chemistry • Biology • Mathematics • English • Language Learning • Coding

## Project structure

```
bot.py            — Entry point, registers all handlers
config.py         — Environment config
database/
  db.py           — SQLite helpers (users, sessions, progress)
handlers/
  start.py        — /start, /help
  qa.py           — /ask + free-text Q&A
  explain.py      — /explain
  quiz.py         — /quiz with inline keyboard answers
  flashcards.py   — /flashcards with flip/next/stop buttons
  progress.py     — /progress
  language.py     — /language preference
services/
  gemini_service.py — Gemini API wrapper (Q&A, quiz, explain, flashcards)
utils/
  helpers.py      — Shared keyboards and helpers
```

## User preferences

- Keep all handlers in separate files under `handlers/`
- Use SQLite for persistence (no external DB required)
- Multilingual: respond in the user's language by default
