import requests
import json

from config import (
    OLLAMA_URL,
    OLLAMA_MODEL
)


def generate_quiz(topic: str):

    prompt = f"""
You are an expert Computer Science tutor.

Generate 5 multiple-choice questions about:

Topic: {topic}

Return ONLY valid JSON.

Format:

{{
    "questions":[
        {{
            "question":"Question here",
            "options":[
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer":"Correct Option"
        }}
    ]
}}

Do not write explanations.
Do not use markdown.
Return JSON only.
"""

    response = requests.post(

        OLLAMA_URL,

        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

    )

    if response.status_code != 200:

        return {"questions": []}

    text = response.json()["response"].strip()

    try:

        return json.loads(text)

    except Exception:

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:

            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass

    return {"questions": []}