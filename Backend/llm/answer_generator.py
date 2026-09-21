import ollama

from config import (
    OLLAMA_KEEP_ALIVE,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
)


def generate_answer(prompt, num_predict=None):
    """
    Single LLM call site for the whole application.

    num_predict is the MAXIMUM answer length (set from the marks
    detected in the question) and is deliberately left untouched
    here - shrinking it would shorten academic answers, which is
    not an acceptable way to buy speed.

    Two options are set that Ollama otherwise defaults badly for:

    num_ctx    - the context window. Ollama's default of ~2048 is
                 smaller than a large grounded prompt plus a
                 10-mark answer budget, and when it overflows the
                 prompt is truncated silently. The Knowledge Graph
                 facts sit at the top of the prompt, so they were
                 the first thing lost - the model then answered
                 from its own memory instead of from the graph.

    keep_alive - how long the model stays resident afterwards.
                 Ollama unloads after 5 idle minutes by default,
                 so the first question after any pause paid the
                 model-load cost again before generating a token.
    """

    options = {
        "num_ctx": OLLAMA_NUM_CTX,
    }

    if num_predict is not None:
        options["num_predict"] = num_predict

    keep_alive = OLLAMA_KEEP_ALIVE
    try:
        keep_alive = int(keep_alive)
    except (ValueError, TypeError):
        pass

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options=options,
        keep_alive=keep_alive,
    )

    return response["message"]["content"]
