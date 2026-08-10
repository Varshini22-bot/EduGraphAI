import json
import re


def format_answer(response):

    try:
        return json.loads(response)

    except Exception:

        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:

            try:
                return json.loads(match.group())

            except Exception:
                pass

    return {
        "definition": "",
        "working": "",
        "advantages": [],
        "disadvantages": [],
        "applications": []
    }