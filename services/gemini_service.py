"""Wrapper around Google Gemini API."""
import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)


def _chat(prompt: str) -> str:
    response = _model.generate_content(prompt)
    return response.text.strip()


def _extract_json(text: str) -> str:
    """Strip markdown code fences if present."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


# ── Public API ────────────────────────────────────────────────────────────────

def answer_question(question: str, user_lang: str = "auto") -> str:
    lang_hint = f"Respond in the same language as the question." if user_lang == "auto" \
        else f"Respond in {user_lang}."
    prompt = f"""{lang_hint}

A student asks: {question}

Give a thorough, clear educational answer. Use bullet points or steps where helpful.
For math/physics use plain text notation (e.g. x^2 for x squared). For code use triple backticks."""
    return _chat(prompt)


def explain_concept(concept: str, user_lang: str = "auto") -> str:
    lang_hint = f"Respond in the same language as this text: '{concept}'." if user_lang == "auto" \
        else f"Respond in {user_lang}."
    prompt = f"""{lang_hint}

Explain the following concept in simple, engaging terms a student will understand:
"{concept}"

Structure your explanation as:
1. Simple one-sentence definition
2. Analogy or real-world example
3. Key details (3–5 bullet points)
4. One quick quiz question to check understanding (with answer)"""
    return _chat(prompt)


def generate_quiz(topic: str, num_questions: int = 5, user_lang: str = "auto") -> list[dict]:
    """Return a list of {question, options: [A,B,C,D], answer, explanation} dicts."""
    lang_hint = f"Write the quiz in the same language as this topic name: '{topic}'." if user_lang == "auto" \
        else f"Write the quiz in {user_lang}."
    prompt = f"""{lang_hint}

Generate {num_questions} multiple-choice quiz questions about: "{topic}"

Return ONLY a JSON array (no other text) where each element has:
{{
  "question": "...",
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "answer": "A",
  "explanation": "..."
}}

The "answer" field must be exactly one letter: A, B, C, or D."""

    raw = _chat(prompt)
    data = json.loads(_extract_json(raw))
    if not isinstance(data, list):
        raise ValueError("Gemini did not return a JSON array for quiz.")
    return data


def generate_flashcards(topic: str, num_cards: int = 8, user_lang: str = "auto") -> list[dict]:
    """Return a list of {front, back} dicts."""
    lang_hint = f"Write in the same language as this topic name: '{topic}'." if user_lang == "auto" \
        else f"Write in {user_lang}."
    prompt = f"""{lang_hint}

Create {num_cards} study flashcards for: "{topic}"

Return ONLY a JSON array (no other text) where each element has:
{{
  "front": "Term or question",
  "back": "Definition or answer"
}}"""

    raw = _chat(prompt)
    data = json.loads(_extract_json(raw))
    if not isinstance(data, list):
        raise ValueError("Gemini did not return a JSON array for flashcards.")
    return data


def detect_subject(text: str) -> str:
    """Best-effort subject classification for progress tracking."""
    prompt = f"""Classify the following text into exactly one of these subjects:
Higher Mathematics, Physics, Chemistry, Biology, Mathematics, English, Language Learning, Coding, General

Text: "{text[:300]}"

Reply with only the subject name, nothing else."""
    return _chat(prompt).strip()
