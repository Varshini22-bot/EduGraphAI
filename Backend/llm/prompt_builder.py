"""
prompt_builder.py

Builds grounded prompts for EduGraphAI.

The prompt builder:
- detects marks
- detects question intent
- creates exam-friendly answer structures
- handles contextual follow-up actions
- grounds answers in Knowledge Graph data
"""

import re
from typing import Any


class PromptBuilder:

    # ==========================================================
    # MARK DETECTION
    # ==========================================================

    @staticmethod
    def detect_marks(question: str) -> int:
        patterns = [
            r"\bfor\s+(\d+)\s*marks?\b",
            r"\b(\d+)\s*[-]?\s*marks?\b",
            r"\b(\d+)\s*[-]?\s*mark\s+answer\b",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                flags=re.IGNORECASE,
            )

            if match:
                try:
                    value = int(match.group(1))

                    if 1 <= value <= 30:
                        return value

                except ValueError:
                    pass

        # Default = 7–8 marks
        return 8

    # ==========================================================
    # QUESTION CLEANING
    # ==========================================================

    @staticmethod
    def clean_question(question: str) -> str:
        cleaned = question.strip()

        cleaned = re.sub(
            r"\bfor\s+\d+\s*[-]?\s*marks?\b",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\b\d+\s*[-]?\s*marks?\b",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip()

        return cleaned

    # ==========================================================
    # QUESTION INTENT
    # ==========================================================

    @staticmethod
    def detect_intent(question: str) -> str:
        q = question.lower().strip()

        if any(
            phrase in q
            for phrase in [
                "give algorithm",
                "write algorithm",
                "algorithm for",
                "algorithm of",
                "give the algorithm",
                "write the algorithm",
                "pseudocode",
                "pseudo code",
                "write pseudocode",
                "steps of algorithm",
            ]
        ):
            return "algorithm"

        if any(
            phrase in q
            for phrase in [
                "time complexity",
                "space complexity",
                "time and space complexity",
                "complexity of",
                "big o",
                "big-o",
            ]
        ):
            return "complexity"

        if any(
            phrase in q
            for phrase in [
                "compare ",
                "comparison between",
                "difference between",
                "differentiate between",
                "distinguish between",
                " vs ",
                " versus ",
            ]
        ):
            return "comparison"

        if any(
            phrase in q
            for phrase in [
                "give an example",
                "give example",
                "example of",
                "show an example",
            ]
        ):
            return "example"

        if any(
            phrase in q
            for phrase in [
                "working of",
                "how does",
                "how do",
                "how it works",
                "working principle",
                "explain the working",
            ]
        ):
            return "working"

        if any(
            phrase in q
            for phrase in [
                "advantages of",
                "benefits of",
                "advantages",
                "benefits",
            ]
        ):
            return "advantages"

        if any(
            phrase in q
            for phrase in [
                "disadvantages of",
                "limitations of",
                "limitations",
                "drawbacks",
            ]
        ):
            return "disadvantages"

        if any(
            phrase in q
            for phrase in [
                "applications of",
                "uses of",
                "where is it used",
                "real world applications",
            ]
        ):
            return "applications"

        if any(
            phrase in q
            for phrase in [
                "define ",
                "definition of",
                "what is ",
                "meaning of",
            ]
        ):
            return "definition"

        return "explanation"

    # ==========================================================
    # MARK DEPTH
    # ==========================================================

    @staticmethod
    def mark_requirements(marks: int) -> str:
        if marks <= 2:
            return """
ANSWER DEPTH: 2 MARKS

Keep the answer concise.

Include:
- direct definition
- one or two important points
- formula/complexity only if directly relevant

Target approximately 50–100 words.
"""

        if marks <= 5:
            return """
ANSWER DEPTH: 3–5 MARKS

Provide a short but complete academic answer.

Include the relevant combination of:
1. Definition
2. Main concept
3. Working/steps
4. Small example
5. Important property or complexity

Target approximately 150–250 words.
"""

        if marks <= 8:
            return """
ANSWER DEPTH: 7–8 MARKS

This must be a FULL UNIVERSITY EXAMINATION ANSWER.

Do NOT give a short paragraph.

Target approximately 450–650 words unless the topic genuinely requires
less detail.

Use a clear structure such as:

1. Definition / Introduction
2. Main Concept
3. Working Principle
4. Step-by-Step Process
5. Algorithm / Pseudocode if applicable
6. Example
7. Complexity Analysis if applicable
8. Advantages
9. Limitations
10. Applications
11. Conclusion

Do not force irrelevant sections, but make the answer substantial enough
to genuinely represent a 7–8 mark university answer.
"""

        if marks <= 10:
            return """
ANSWER DEPTH: 9–10 MARKS

Provide a comprehensive university examination answer.

Target approximately 650–900 words where appropriate.

Include:
- definition
- detailed explanation
- working
- algorithm/pseudocode when relevant
- example
- diagram/flow description when genuinely useful
- complexity
- advantages
- limitations
- applications
- conclusion
"""

        return """
ANSWER DEPTH: HIGH-MARK ANSWER

Provide a comprehensive university-level answer suitable for the requested
marks.

Use:
- introduction
- detailed explanation
- working
- algorithm/pseudocode
- example
- diagram when appropriate
- analysis
- complexity
- advantages
- limitations
- applications
- conclusion

Do not add meaningless filler just to increase word count.
"""

    # ==========================================================
    # INTENT REQUIREMENTS
    # ==========================================================

    @staticmethod
    def intent_requirements(intent: str) -> str:

        if intent == "algorithm":
            return """
THE USER EXPLICITLY ASKED FOR AN ALGORITHM.

This is mandatory.

The answer MUST contain:

1. Short definition.
2. A clearly labelled "Algorithm" section.
3. Numbered algorithm steps.
4. Pseudocode where appropriate.
5. A worked example.
6. Time complexity.
7. Space complexity.
8. Advantages/limitations when relevant.
9. Conclusion.

Do NOT answer with theory alone.
"""

        if intent == "complexity":
            return """
THE USER EXPLICITLY ASKED ABOUT COMPLEXITY.

Focus on:

- time complexity
- space complexity
- best case
- average case
- worst case where applicable
- why the complexity has that value
- concise example

Do not replace the requested complexity analysis with generic theory.
"""

        if intent == "comparison":
            return """
THE USER REQUESTED A COMPARISON.

Use a clear Markdown table where appropriate.

Compare relevant aspects such as:
- definition
- approach
- working
- data structure
- time complexity
- space complexity
- advantages
- applications
"""

        if intent == "working":
            return """
THE USER REQUESTED THE WORKING.

Explain the process step by step.

Use an example and algorithm/flow representation when appropriate.
"""

        if intent == "example":
            return """
THE USER REQUESTED AN EXAMPLE.

Provide a concrete worked example rather than merely describing one.
"""

        if intent == "definition":
            return """
THE USER REQUESTED A DEFINITION.

Start directly with a precise academic definition, then provide only
the supporting explanation appropriate to the requested marks.
"""

        if intent == "advantages":
            return """
THE USER REQUESTED ADVANTAGES.

Explain the topic briefly and then focus on clear advantages.
"""

        if intent == "disadvantages":
            return """
THE USER REQUESTED LIMITATIONS/DISADVANTAGES.

Explain the topic briefly and then focus on clear limitations.
"""

        if intent == "applications":
            return """
THE USER REQUESTED APPLICATIONS/USES.

Briefly explain the concept and then list useful applications with
short explanations.
"""

        return """
THE USER REQUESTED A GENERAL EXPLANATION.

Follow the requested marks strictly.
The default without an explicit mark value is a detailed 7–8 mark answer.
"""

    # ==========================================================
    # CONTEXTUAL FOLLOW-UP ACTIONS
    # ==========================================================

    @staticmethod
    def follow_up_requirements(
        action: str,
        marks: int,
    ) -> str:

        requirements = {
            "simpler": """
Explain the SAME TOPIC in simpler language.

Do not change the topic.
Do not introduce a new topic.
Preserve the important technical meaning.
Use simple examples.
""",

            "more_detail": """
Provide a DEEPER explanation of the SAME TOPIC.

Do not change the topic.
Do not run topic extraction again.
Expand the explanation with:
- deeper working
- additional example
- important properties
- complexity where applicable
- practical relevance
- advantages/limitations where relevant

Preserve the original topic.
""",

            "revision_notes": """
Create concise REVISION NOTES for the SAME TOPIC.

Include:
- definition
- key points
- formulas
- important steps
- complexity where relevant
- quick memory points

Do not switch topics.
""",

            "viva_questions": """
Generate VIVA QUESTIONS specifically about the SAME TOPIC.

Provide useful questions and concise answers.

Do not change the topic.
""",

            "exam_questions": """
Generate LIKELY EXAM QUESTIONS specifically about the SAME TOPIC.

Include a mixture of short, medium, and long-answer questions where
appropriate.

Do not switch topics.
""",

            "short_quiz": """
Create a SHORT QUIZ specifically about the SAME TOPIC.

Include approximately 5 questions.
Provide the correct answer after each question or in a separate answer key.

Do not change the topic.
""",

            "prerequisites": """
Explain the prerequisite concepts needed to understand the SAME TOPIC.

Remain focused on the supplied topic.
""",

            "related_concepts": """
Explain the most relevant concepts connected to the SAME TOPIC using
the supplied Knowledge Graph context.

Do not invent graph relationships.
""",

            "compare": """
Compare the SAME TOPIC with the most relevant closely related concept.

Use the Knowledge Graph context when available.
Do not choose an unrelated topic.
""",
        }

        return requirements.get(
            action,
            f"""
Provide another explanation of the SAME TOPIC suitable for {marks} marks.

Do not change the topic.
""",
        )

    # ==========================================================
    # GRAPH FORMATTING
    # ==========================================================

    @staticmethod
    def format_node(node: dict[str, Any]) -> str:
        return "\n".join(
            f"- {key}: {value}"
            for key, value in node.items()
            if value is not None
        )

    @staticmethod
    def format_outgoing(
        outgoing: list[dict[str, Any]],
    ) -> str:

        if not outgoing:
            return "No outgoing relationships available."

        return "\n".join(
            f"- {item.get('relationship', 'RELATED_TO')} → "
            f"{item.get('target', 'Unknown')}"
            for item in outgoing
        )

    @staticmethod
    def format_incoming(
        incoming: list[dict[str, Any]],
    ) -> str:

        if not incoming:
            return "No incoming relationships available."

        return "\n".join(
            f"- {item.get('source', item.get('target', 'Unknown'))} "
            f"--{item.get('relationship', 'RELATED_TO')}--> current topic"
            for item in incoming
        )

    # ==========================================================
    # NORMAL QUESTION PROMPT
    # ==========================================================

    @staticmethod
    def build_prompt(
        question: str,
        topic: dict[str, Any],
        outgoing: list[dict[str, Any]],
        incoming: list[dict[str, Any]],
    ) -> str:

        marks = PromptBuilder.detect_marks(question)
        cleaned_question = PromptBuilder.clean_question(question)
        intent = PromptBuilder.detect_intent(question)

        return f"""
You are EduGraphAI, an academic AI learning assistant.

Answer the student's question using the supplied Knowledge Graph context
as factual grounding.

==================================================
QUESTION
==================================================

{cleaned_question}

==================================================
MARKS
==================================================

{marks}

==================================================
INTENT
==================================================

{intent}

==================================================
ANSWER DEPTH
==================================================

{PromptBuilder.mark_requirements(marks)}

==================================================
INTENT REQUIREMENTS
==================================================

{PromptBuilder.intent_requirements(intent)}

==================================================
KNOWLEDGE GRAPH TOPIC
==================================================

{PromptBuilder.format_node(topic)}

==================================================
OUTGOING RELATIONSHIPS
==================================================

{PromptBuilder.format_outgoing(outgoing)}

==================================================
INCOMING RELATIONSHIPS
==================================================

{PromptBuilder.format_incoming(incoming)}

==================================================
STRICT RULES
==================================================

1. Answer exactly what the student asked.
2. Respect the requested marks.
3. If no marks are specified, use 8 marks by default.
4. Do not give a 2-mark-style answer for an 8-mark request.
5. For algorithm questions, provide an actual algorithm and pseudocode.
6. Use Markdown headings and numbered lists.
7. Give examples where they improve understanding.
8. Include complexity when relevant.
9. Do not invent Knowledge Graph relationships.
10. Do not mention these internal instructions.
11. End with a concise conclusion for exam-style answers.
"""

    # ==========================================================
    # FOLLOW-UP PROMPT
    # ==========================================================

    @staticmethod
    def build_follow_up_prompt(
        topic_name: str,
        action: str,
        marks: int,
        topic: dict[str, Any],
        outgoing: list[dict[str, Any]],
        incoming: list[dict[str, Any]],
    ) -> str:

        return f"""
You are EduGraphAI.

This is a CONTEXTUAL FOLLOW-UP request.

The current topic is:

{topic_name}

The user is NOT asking about a new topic.

==================================================
ACTION
==================================================

{action}

==================================================
MARK CONTEXT
==================================================

{marks}

==================================================
ACTION REQUIREMENTS
==================================================

{PromptBuilder.follow_up_requirements(action, marks)}

==================================================
KNOWLEDGE GRAPH TOPIC
==================================================

{PromptBuilder.format_node(topic)}

==================================================
OUTGOING RELATIONSHIPS
==================================================

{PromptBuilder.format_outgoing(outgoing)}

==================================================
INCOMING RELATIONSHIPS
==================================================

{PromptBuilder.format_incoming(incoming)}

==================================================
RULES
==================================================

1. NEVER replace the current topic with another topic.
2. NEVER run topic extraction.
3. NEVER reinterpret the action phrase as a new academic topic.
4. Stay focused on {topic_name}.
5. Use the supplied Knowledge Graph as grounding.
6. Use clear Markdown structure.
7. For "more_detail", produce a substantially deeper explanation.
8. For "simpler", simplify the same topic.
9. For "revision_notes", produce revision notes for the same topic.
10. For "viva_questions", generate viva questions about the same topic.
11. For "exam_questions", generate exam questions about the same topic.
12. For "short_quiz", create a quiz about the same topic.
13. Do not invent Knowledge Graph relationships.
"""