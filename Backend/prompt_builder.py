def build_prompt(topic, graph_data):

    context = ""

    for item in graph_data:
        context += f"{item['relation']} -> {item['related']}\n"

    prompt = f"""
You are a Computer Science tutor.

Topic: {topic}

Knowledge Graph Facts:
{context}

Rules:

1. If CONTAINS relationships exist,
   explain those as types/subtopics.

2. If EVALUATES relationships exist,
   explain them as performance metrics.

3. Mention every graph fact at least once.

4. Use the graph facts while answering.

Answer format:

1. Definition
2. Working
3. Types/Subtopics
4. Evaluation Metrics
5. Advantages
6. Applications
7. Related Concepts
"""

    return prompt