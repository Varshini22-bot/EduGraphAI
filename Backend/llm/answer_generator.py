import ollama

from config import OLLAMA_MODEL


def generate_answer(prompt):

    response = ollama.chat(

        model=OLLAMA_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    return response["message"]["content"]