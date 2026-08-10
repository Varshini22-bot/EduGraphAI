from topic_extractor import extract_topic

while True:

    question = input("Question: ")

    topic = extract_topic(question)

    print("Detected Topic:", topic)