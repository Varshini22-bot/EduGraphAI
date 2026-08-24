import ollama

from config import OLLAMA_MODEL


def generate_answer(prompt, num_predict=None):
    options = {}
    if num_predict is not None:
        options["num_predict"] = num_predict

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options=options,
    )

    return response["message"]["content"]
