from learning_path import get_learning_path

topic = input("Topic: ")

path = get_learning_path(topic)

print("\nLearning Path:\n")

for i, item in enumerate(path, start=1):
    print(f"{i}. {item}")