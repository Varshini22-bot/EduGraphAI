from topic_extractor import extract_topic

while True:

    question = input("Question: ")

    if question.lower() == "exit":
        break

    topic = extract_topic(question)

    print("Detected Topic:", topic)
    print()