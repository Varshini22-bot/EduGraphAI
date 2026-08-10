def extract_topic(question):

    question = question.lower()

    remove_words = [
        "what is",
        "explain",
        "tell me about",
        "describe",
        "define"
    ]

    for word in remove_words:
        question = question.replace(word, "")

    question = question.replace("?", "")

    return question.strip()