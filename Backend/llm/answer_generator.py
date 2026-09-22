import requests
import ollama

from config import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_BASE_URL,
    LLM_API_KEY,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
)


def _generate_ollama(prompt: str, num_predict: int = None) -> str:
    """Generate answer using local Ollama daemon."""
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
        model=LLM_MODEL or OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options=options,
        keep_alive=keep_alive,
    )

    return response["message"]["content"]


def _generate_openai_compatible(prompt: str, num_predict: int = None) -> str:
    """Generate answer using hosted OpenAI-compatible REST API (Groq, OpenAI, Gemini, etc.)."""
    if not LLM_API_KEY or not LLM_API_KEY.strip():
        raise ValueError(
            f"LLM_API_KEY environment variable is required when LLM_PROVIDER is set to '{LLM_PROVIDER}'."
        )

    base_url = (LLM_BASE_URL or "").rstrip("/")
    if not base_url:
        raise ValueError(
            f"LLM_BASE_URL must be specified for OpenAI-compatible provider '{LLM_PROVIDER}'."
        )

    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    # For cloud LLMs, ensure ample token headroom so reasoning tokens (e.g. on Groq)
    # or detailed exam sections never cause premature finish_reason: length truncation.
    if num_predict is not None:
        payload["max_tokens"] = max(num_predict, 3200)
    else:
        payload["max_tokens"] = 3500

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        choice = data["choices"][0]
        finish_reason = choice.get("finish_reason")
        if finish_reason == "length":
            print(f"[WARN] LLM answer was truncated by token limit (finish_reason: length)!")
        return choice["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Cloud LLM request to '{LLM_PROVIDER}' failed: {e}") from e


def generate_answer(prompt, num_predict=None):
    """
    Single LLM call site for the whole application.

    Dispatches to:
    - Ollama (local daemon) when LLM_PROVIDER='ollama'
    - Hosted OpenAI-compatible API (Groq, OpenAI, Gemini, OpenRouter) otherwise.

    num_predict is the MAXIMUM answer length (set from the marks
    detected in the question). When using Ollama it maps to 'num_predict',
    and when using hosted cloud APIs it maps to 'max_tokens'.
    """
    if LLM_PROVIDER == "ollama":
        return _generate_ollama(prompt, num_predict=num_predict)
    else:
        return _generate_openai_compatible(prompt, num_predict=num_predict)
