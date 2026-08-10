from query_processor import extract_topic

question = input("Question: ")

topic = extract_topic(question)

print(topic)