from graph.recommendation import get_recommendations

print()

print("Recommendations")

print("----------------")

result = get_recommendations(
    "Quick Sort"
)

for item in result:

    print(item)