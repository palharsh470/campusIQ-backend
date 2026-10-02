from django.conf import settings
from google import genai
import json

_client = None

def get_client():
    global _client

    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        _client =  genai.Client(api_key=settings.GEMINI_API_KEY)

    return _client

def build_prompt(content, num_questions, include_skill):
    skill_instruction = (
        'Each question object must also include "suggested_skill": a short (2-3 word) '
        'name for the specific concept it tests (e.g. "Binary Search", "Recursion Basics").'
        if include_skill else ""
    )
    return f"""You are creating a multiple-choice quiz for college students based on the lecture content below.

Lecture content:
\"\"\"
{content}
\"\"\"

Generate exactly {num_questions} multiple-choice questions that test understanding of this content.
Respond with ONLY a JSON array (no markdown, no extra text) where each item has this exact shape:
{{
  "text": "the question",
  "options": [
    {{"text": "option text", "is_correct": true}},
    {{"text": "option text", "is_correct": false}},
    {{"text": "option text", "is_correct": false}},
    {{"text": "option text", "is_correct": false}}
  ]
}}
Each question must have exactly 4 options with exactly one is_correct: true.
{skill_instruction}
"""

def generate_questions(content, num_questions, include_skill=False):
    client = get_client()
    prompt = build_prompt(content, num_questions, include_skill)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )

    questions = json.loads(response.text)

    cleaned = []
    for q in questions:
        options = q.get("options", [])
        correct_count = sum(1 for o in options if o.get("is_correct"))
        if not q.get("text") or len(options) != 4 or correct_count != 1:
            continue   
        cleaned.append(q)

    if not cleaned:
        raise ValueError("AI didn't return any usable questions.")

    return cleaned