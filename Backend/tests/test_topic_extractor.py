from llm.topic_extractor import TopicExtractor


questions = [

    "Explain Merge Sort",

    "What is Quick Sort?",

    "Tell me about Binary Search",

    "How does Algorithm work?",

    "Quantum Computing"

]


for question in questions:

    topic = TopicExtractor.extract_topic(question)

    print("--------------------------------")

    print("Question:", question)

    print("Detected Topic:", topic)