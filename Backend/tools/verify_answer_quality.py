"""
verify_answer_quality.py

Phase 5 LIVE verification. Unlike tests/test_answer_quality_offline.py,
this one needs Neo4j AND Ollama running, because it asks the real
RAGService for real answers and then inspects what came back.

What it checks, per question:

  status   - the pipeline returned an answer at all
  topic    - the Knowledge Graph node the answer was grounded on
  sections - which of the expected exam-answer sections appear
  drift    - whether a follow-up answer wandered off its topic
  words    - answer length, to catch a 2-mark stub sold as an 8-mark answer

The section and drift checks are HEURISTICS - they scan the generated
Markdown for headings and keywords. They are good at catching a section
that is completely missing or an answer that has changed subject, but
they cannot judge whether the content is academically correct. Use
--save and read a few answers before signing anything off.

Run from Backend/:

    python -m tools.verify_answer_quality
    python -m tools.verify_answer_quality --save answers.md
    python -m tools.verify_answer_quality --only follow-ups

The first question is slow (Ollama loads the model); OLLAMA_KEEP_ALIVE
keeps it warm for the rest.
"""

import argparse
import os
import sys
import time

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from llm.rag_service import RAGService  # noqa: E402


# ==============================================================
# EXPECTED SECTIONS
#
# The eight elements the Phase 5 brief asks a marks-based answer to
# cover. Each is a list of alternative wordings, because the model
# picks its own heading text ("Working Principle" / "How It Works").
#
# `optional` marks the sections that legitimately do not apply to
# every topic - the brief says not to force every section onto every
# question, so their absence is reported but not counted as a failure.
# ==============================================================

SECTIONS = [
    ("Definition",    ["definition", "introduction", "what is"],           False),
    ("Working",       ["working", "how it works", "principle", "process"], False),
    ("Algorithm",     ["algorithm", "pseudocode", "pseudo code"],          True),
    ("Steps",         ["step", "procedure"],                               True),
    ("Example",       ["example", "illustration", "worked"],               False),
    ("Complexity",    ["complexity", "big o", "o(log", "o(n"],             True),
    ("Advantages",    ["advantage", "benefit", "disadvantage",
                       "limitation", "drawback"],                          True),
    ("Conclusion",    ["conclusion", "summary", "in summary"],             False),
]


def find_sections(answer: str) -> set:
    """Which expected sections appear in the answer.

    Headings are preferred, but plain bold or inline mentions count too -
    the model does not always emit '##' for every section.
    """

    lowered = answer.lower()

    found = set()

    for name, keywords, _optional in SECTIONS:
        if any(keyword in lowered for keyword in keywords):
            found.add(name)

    return found


def word_count(answer: str) -> int:
    return len(answer.split())


# ==============================================================
# EXPECTED LENGTH PER MARKS
#
# Lower bounds only, and generous ones. The point is to catch an
# 8-mark request answered in two sentences, not to police prose.
# Upper bounds are omitted because a slightly long answer is not a
# defect for a student revising.
# ==============================================================

MIN_WORDS = {
    2: 30,
    5: 100,
    8: 300,
    10: 450,
    15: 550,
}


# ==============================================================
# TEST CASES
# ==============================================================

# The five examples named in the Phase 5 brief, plus one more per
# subject so every subject in the graph is exercised.
NORMAL_CASES = [
    ("Explain Binary Search.",           "Binary Search",      8),
    ("Explain Quick Sort.",              "Quick Sort",         8),
    ("What is Machine Learning?",        "Machine Learning",   8),
    ("Explain Divide and Conquer.",      "Divide and Conquer", 8),
    ("What is an Operating System?",     "Operating System",   8),
    ("Explain the OSI Model",            "OSI Model",          8),
    ("Explain Deadlock",                 "Deadlock",           8),
    ("Explain the Waterfall Model",      "Waterfall Model",    8),
]

MARKS_CASES = [
    ("Explain Binary Search for 2 marks",   "Binary Search", 2),
    ("Explain Binary Search for 5 marks",   "Binary Search", 5),
    ("Explain Binary Search for 8 marks",   "Binary Search", 8),
    ("Explain Binary Search for 10 marks",  "Binary Search", 10),
    ("Explain Quick Sort for 8 marks",      "Quick Sort",    8),
    # A conceptual topic at 8 marks - this is where the model used to
    # invent an algorithm and a complexity analysis for something that
    # has neither. Both are optional sections, so their ABSENCE here is
    # the good outcome; check the printed answer if they appear.
    ("What is Machine Learning? Answer for 8 marks",
     "Machine Learning", 8),
]

# Exactly the five follow-ups the brief names, in the wire format the
# frontend builds (em dash U+2014). The topic must stay Binary Search.
FOLLOW_UP_CASES = [
    ("Binary Search — explain it more simply",            "Binary Search"),
    ("Binary Search — give a more detailed explanation",  "Binary Search"),
    ("Binary Search — create revision notes",             "Binary Search"),
    ("Binary Search — generate viva questions",           "Binary Search"),
    ("Binary Search — generate likely exam questions",    "Binary Search"),
]

# Words that should never dominate a Binary Search answer. These are the
# specific unrelated topics the brief calls out, plus a few neighbours
# from other subjects that a drifting model tends to reach for.
DRIFT_MARKERS = [
    "cocomo",
    "sepm",
    "waterfall model",
    "requirement engineering",
    "software project management",
    "risk management",
]


def check_drift(answer: str, topic: str) -> list:
    """Returns the drift problems found, empty list if the answer stayed
    on topic. Drift is judged two ways: the topic must actually be
    discussed, and unrelated subjects must not be."""

    lowered = answer.lower()

    problems = []

    if topic.lower() not in lowered:
        problems.append(f"answer never mentions {topic!r}")

    for marker in DRIFT_MARKERS:
        # A passing mention is fine; repeated use means the answer has
        # changed subject.
        if lowered.count(marker) >= 2:
            problems.append(f"drifted to {marker!r}")

    return problems


# ==============================================================
# RUNNER
# ==============================================================

class Result:
    def __init__(self, question):
        self.question = question
        self.ok = True
        self.problems = []
        self.topic = None
        self.words = 0
        self.sections = set()
        self.missing = []
        self.seconds = 0.0
        self.answer = ""

    def fail(self, message):
        self.ok = False
        self.problems.append(message)


def run_case(question, expected_topic, marks=None, check_sections=True):
    result = Result(question)

    start = time.perf_counter()

    try:
        payload = RAGService.answer(question)
    except Exception as error:
        result.seconds = time.perf_counter() - start
        result.fail(f"raised {type(error).__name__}: {error}")
        return result

    result.seconds = time.perf_counter() - start

    if not payload.get("status"):
        result.fail(
            f"status False - {payload.get('message', 'no message')}"
        )
        result.topic = payload.get("topic")
        return result

    answer = payload.get("answer") or ""

    result.answer = answer
    result.topic = payload.get("topic")
    result.words = word_count(answer)
    result.sections = find_sections(answer)

    if result.topic != expected_topic:
        result.fail(
            f"topic {result.topic!r}, expected {expected_topic!r}"
        )

    for problem in check_drift(answer, expected_topic):
        result.fail(problem)

    if marks is not None:
        minimum = MIN_WORDS.get(marks, 0)

        if result.words < minimum:
            result.fail(
                f"{result.words} words, expected at least "
                f"{minimum} for {marks} marks"
            )

    if check_sections:
        for name, _keywords, optional in SECTIONS:
            if name in result.sections:
                continue

            if optional:
                result.missing.append(f"{name}?")
            else:
                result.missing.append(name)
                result.fail(f"missing required section: {name}")

    return result


def print_table(title, results):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

    header = (
        f"{'question':<46}"
        f"{'topic':<22}"
        f"{'words':>6}"
        f"{'sec':>5}"
        f"{'time':>8}"
        f"  status"
    )

    print(header)
    print("-" * len(header))

    for result in results:
        question = result.question

        if len(question) > 44:
            question = question[:41] + "..."

        topic = str(result.topic)

        if len(topic) > 20:
            topic = topic[:17] + "..."

        print(
            f"{question:<46}"
            f"{topic:<22}"
            f"{result.words:>6}"
            f"{len(result.sections):>5}"
            f"{result.seconds:>7.1f}s"
            f"  {'OK' if result.ok else 'FAIL'}"
        )

        if result.missing:
            print(f"{'':<46}absent: {', '.join(result.missing)}")

        for problem in result.problems:
            print(f"{'':<46}!! {problem}")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 5 live answer-quality verification.",
    )

    parser.add_argument(
        "--only",
        choices=["normal", "marks", "follow-ups"],
        help="run only one group instead of all three",
    )

    parser.add_argument(
        "--save",
        metavar="FILE",
        help="write every generated answer to FILE for manual review",
    )

    args = parser.parse_args()

    groups = []

    if args.only in (None, "normal"):
        groups.append((
            "NORMAL QUESTIONS (no marks given - 7-8 mark default)",
            [
                (question, topic, marks, True)
                for question, topic, marks in NORMAL_CASES
            ],
        ))

    if args.only in (None, "marks"):
        groups.append((
            "MARKS-BASED QUESTIONS",
            [
                (question, topic, marks, marks >= 5)
                for question, topic, marks in MARKS_CASES
            ],
        ))

    if args.only in (None, "follow-ups"):
        # Follow-ups produce notes, viva questions and quizzes, none of
        # which are supposed to have an exam-answer section structure -
        # so only the topic and drift checks apply here.
        groups.append((
            "CONTEXTUAL FOLLOW-UPS (topic must stay Binary Search)",
            [
                (question, topic, None, False)
                for question, topic in FOLLOW_UP_CASES
            ],
        ))

    all_results = []

    for title, cases in groups:
        results = [
            run_case(question, topic, marks, sections)
            for question, topic, marks, sections in cases
        ]

        print_table(title, results)

        all_results.extend(results)

    passed = sum(1 for r in all_results if r.ok)
    failed = len(all_results) - passed

    print("\n" + "=" * 100)
    print(f"RESULT: {passed} passed, {failed} failed")
    print(
        "'sec' counts how many of the 8 expected sections were detected. "
        "Optional sections marked '?' are\nallowed to be absent - a "
        "conceptual topic has no algorithm or complexity to report."
    )
    print("=" * 100)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as handle:
            for result in all_results:
                handle.write(f"# {result.question}\n\n")
                handle.write(
                    f"topic: {result.topic} | words: {result.words} | "
                    f"time: {result.seconds:.1f}s | "
                    f"{'OK' if result.ok else 'FAIL'}\n\n"
                )

                if result.problems:
                    handle.write(
                        "problems: " + "; ".join(result.problems) + "\n\n"
                    )

                handle.write(result.answer + "\n\n---\n\n")

        print(f"\nAnswers written to {args.save}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
