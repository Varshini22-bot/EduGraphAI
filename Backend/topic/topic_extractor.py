import re
from topic.load_topics import get_all_topics
from rapidfuzz import process
from rapidfuzz import fuzz


TOPICS = get_all_topics()


def clean_question(question):

    question = question.lower()

    stop_words = [
        "what is",
        "what are",
        "explain",
        "tell me about",
        "define",
        "describe",
        "give me",
        "information about",
        "can you explain",
        "please explain"
    ]

    for word in stop_words:
        question = question.replace(word, "")

    question = re.sub(r"[^\w\s]", "", question)

    return question.strip()


def extract_topic(question):

    cleaned = clean_question(question)

    match = process.extractOne(
        cleaned,
        TOPICS,
        scorer=fuzz.WRatio
    )

    if match:

        topic = match[0]
        score = match[1]

        print("Cleaned Question:", cleaned)
        print("Matched Topic:", topic)
        print("Similarity Score:", score)

        if score >= 75:
            return topic

    return None