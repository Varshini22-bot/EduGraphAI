"""
test_answer_quality_offline.py

Phase 5 verification that does NOT need Neo4j or Ollama running.

Everything checked here is deterministic Python: topic resolution, marks
detection, answer-depth structure, and contextual follow-up detection.
The real graph is replaced by the label list read straight out of
Backend/data/MERGED/master_nodes.csv, which is the same data that was
imported into Neo4j - so a pass here means the routing logic is correct,
and only the LLM wording still needs a live check.

For the live half (real answers from Ollama, section coverage, drift),
use Backend/tools/verify_answer_quality.py instead.

Run from Backend/:

    python -m tests.test_answer_quality_offline

Exit code 0 = all checks passed, 1 = at least one failed.
"""

import csv
import os
import sys
import types


# ==============================================================
# IMPORT GUARD
#
# graph.neo4j_client builds a driver at import time, and
# llm.answer_generator imports the ollama package at import time. On a
# fully installed machine both are harmless (the Neo4j driver is lazy
# and never connects unless a session is opened, and importing ollama
# does not start the server), but in an environment where the packages
# are absent the import would fail before any test could run. Stubbing
# them keeps this suite runnable anywhere, and they stay stubs - no test
# below opens a session or generates an answer. Both stubs RAISE if
# called, so an accidental live call fails loudly instead of passing
# quietly.
# ==============================================================

if "neo4j" not in sys.modules:
    try:
        import neo4j  # noqa: F401
    except ModuleNotFoundError:
        stub = types.ModuleType("neo4j")

        class _StubDriver:
            def session(self, *args, **kwargs):
                raise RuntimeError(
                    "This offline suite must not open a Neo4j session."
                )

            def close(self):
                pass

        class _StubGraphDatabase:
            @staticmethod
            def driver(*args, **kwargs):
                return _StubDriver()

        stub.GraphDatabase = _StubGraphDatabase
        sys.modules["neo4j"] = stub


if "ollama" not in sys.modules:
    try:
        import ollama  # noqa: F401
    except ModuleNotFoundError:
        ollama_stub = types.ModuleType("ollama")

        def _no_generate(*args, **kwargs):
            raise RuntimeError(
                "This offline suite must not call Ollama."
            )

        ollama_stub.generate = _no_generate
        ollama_stub.chat = _no_generate
        sys.modules["ollama"] = ollama_stub


sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from graph.graph_service import GraphService          # noqa: E402
from llm.topic_extractor import TopicExtractor        # noqa: E402
from llm.prompt_builder import PromptBuilder          # noqa: E402
from llm.rag_service import _detect_contextual_action  # noqa: E402


NODES_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "MERGED",
    "master_nodes.csv",
)


def load_labels() -> list[str]:
    """Every topic label in the Knowledge Graph, straight from the CSV."""

    labels = []

    with open(NODES_CSV, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            label = (row.get("label") or "").strip()

            if label:
                labels.append(label)

    return labels


LABELS = load_labels()

# Replace the single Neo4j round trip topic extraction makes. Everything
# downstream of this point is the project's real code, unmodified.
GraphService.get_all_topic_labels = staticmethod(lambda: LABELS)


# ==============================================================
# TINY ASSERT HARNESS
# ==============================================================

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED

    if condition:
        PASSED += 1
        print(f"  PASS  {name}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}")

        if detail:
            print(f"        {detail}")


def section(title: str) -> None:
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


# ==============================================================
# 1. NORMAL QUESTIONS - one topic per subject, plus the named examples
# ==============================================================

NORMAL_QUESTIONS = [
    # The five examples named in the Phase 5 brief.
    ("Explain Binary Search.", "Binary Search"),
    ("Explain Quick Sort.", "Quick Sort"),
    ("What is Machine Learning?", "Machine Learning"),
    ("Explain Divide and Conquer.", "Divide and Conquer"),
    ("What is an Operating System?", "Operating System"),

    # Wider coverage across all six subjects.
    ("Explain Merge Sort", "Merge Sort"),
    ("What is Dynamic Programming?", "Dynamic Programming"),
    ("Explain Linked List", "Linked List"),
    ("What is a Binary Search Tree?", "Binary Search Tree"),
    ("Explain Supervised Learning", "Supervised Learning"),
    ("What is Overfitting?", "Overfitting"),
    ("Explain the OSI Model", "OSI Model"),
    ("What is TCP?", "TCP"),
    ("Explain Deadlock", "Deadlock"),
    ("What is Paging?", "Paging"),
    ("Explain the Waterfall Model", "Waterfall Model"),
    ("What is COCOMO?", "COCOMO Model"),
]


def test_normal_questions() -> None:
    section("1. NORMAL QUESTIONS - topic resolution")

    for question, expected in NORMAL_QUESTIONS:
        actual = TopicExtractor.extract_topic(question)

        check(
            f"{question!r} -> {expected!r}",
            actual == expected,
            f"got {actual!r}",
        )


def test_out_of_graph_returns_none() -> None:
    """A topic that is genuinely absent must resolve to None, not to a
    near-miss node. Answering confidently about the wrong node is worse
    than saying the topic is not in the graph."""

    section("2. OUT-OF-GRAPH QUESTIONS - must return None")

    for question in [
        "Explain Quantum Computing",
        "What is Photosynthesis?",
    ]:
        actual = TopicExtractor.extract_topic(question)

        check(
            f"{question!r} -> None",
            actual is None,
            f"got {actual!r}",
        )


# ==============================================================
# 3. MARKS-BASED QUESTIONS
# ==============================================================

MARKS_QUESTIONS = [
    ("Explain Binary Search for 8 marks", 8, "Binary Search", 950),
    ("Explain Binary Search for 2 marks", 2, "Binary Search", 180),
    ("Explain Quick Sort for 5 marks", 5, "Quick Sort", 400),
    ("Explain Merge Sort for 10 marks", 10, "Merge Sort", 1300),
    ("Explain Deadlock for 15 marks", 15, "Deadlock", 1700),
    # No marks mentioned at all -> the 7-8 mark default.
    ("Explain Binary Search.", 8, "Binary Search", 950),
]


def test_marks_detection() -> None:
    section("3. MARKS-BASED QUESTIONS - marks, topic and token budget")

    for question, marks, topic, budget in MARKS_QUESTIONS:
        detected = PromptBuilder.detect_marks(question)
        resolved = TopicExtractor.extract_topic(question)
        actual_budget = PromptBuilder.token_budget(detected)

        check(
            f"{question!r} -> {marks} marks",
            detected == marks,
            f"got {detected}",
        )

        check(
            f"{question!r} -> topic {topic!r}",
            resolved == topic,
            f"got {resolved!r}",
        )

        check(
            f"{question!r} -> num_predict {budget}",
            actual_budget == budget,
            f"got {actual_budget}",
        )


# The eight structural elements the Phase 5 brief asks an 8-mark answer
# to cover. Each entry is (human name, keywords that must appear in the
# depth instructions). The instructions are what steers the model, so a
# section missing here can never appear reliably in the output.
REQUIRED_SECTIONS = [
    ("Definition / introduction", ["definition"]),
    ("Working / principle", ["working"]),
    ("Algorithm or pseudocode", ["algorithm", "pseudocode"]),
    ("Step-by-step explanation", ["step-by-step", "step by step"]),
    ("Example", ["example"]),
    ("Complexity analysis", ["complexity"]),
    ("Advantages / disadvantages", ["advantages", "disadvantages"]),
    ("Conclusion", ["conclusion"]),
]


def test_eight_mark_structure() -> None:
    section("4. 8-MARK ANSWER DEPTH - required sections present")

    depth = PromptBuilder.mark_requirements(8).lower()

    for name, keywords in REQUIRED_SECTIONS:
        check(
            f"8-mark depth mentions {name}",
            any(keyword in depth for keyword in keywords),
            f"none of {keywords} found",
        )

    # "Do not force every section onto every question if it does not
    # make sense" - the instructions must say to OMIT, not to pad.
    check(
        "8-mark depth tells the model to OMIT inapplicable sections",
        "omitted" in depth and "padding" in depth,
        "no omit-rather-than-pad instruction found",
    )

    check(
        "10-mark depth tells the model to OMIT inapplicable sections",
        "omitted" in PromptBuilder.mark_requirements(10).lower(),
        "no omit instruction found in the 9-10 mark bucket",
    )


def test_prompt_carries_marks_and_graph() -> None:
    """The built prompt must actually contain the detected marks, the
    depth instructions and the graph facts - a prompt that silently
    drops any of these produces a confident but ungrounded answer."""

    section("5. BUILT PROMPT - marks, depth and graph grounding")

    node = {
        "label": "Binary Search",
        "type": "Algorithm",
        "subject": "DSA",
    }

    outgoing = [
        {"relationship": "USES", "target": "Divide and Conquer"},
    ]

    incoming = [
        {"relationship": "PART_OF", "source": "Searching"},
    ]

    prompt = PromptBuilder.build_prompt(
        question="Explain Binary Search for 8 marks",
        topic=node,
        outgoing=outgoing,
        incoming=incoming,
    )

    check(
        "prompt contains the topic label",
        "Binary Search" in prompt,
    )

    check(
        "prompt contains the 7-8 mark depth block",
        "ANSWER DEPTH: 7–8 MARKS" in prompt,
    )

    check(
        "prompt contains the outgoing relationship",
        "Divide and Conquer" in prompt,
    )

    check(
        "prompt contains the incoming relationship",
        "Searching" in prompt,
    )

    check(
        "'for 8 marks' is stripped from the restated question",
        "for 8 marks" not in prompt.split("MARKS")[0],
        "the marks phrase leaked into the QUESTION block",
    )


# ==============================================================
# 6. CONTEXTUAL FOLLOW-UPS
# ==============================================================

# Exactly the five follow-ups named in the Phase 5 brief, in the wire
# format frontend/src/lib/answerIntent.ts builds (em dash U+2014).
FOLLOW_UP_ACTIONS = [
    ("explain it more simply", "simpler"),
    ("give a more detailed explanation", "more_detail"),
    ("create revision notes", "revision_notes"),
    ("generate viva questions", "viva_questions"),
    ("generate likely exam questions", "exam_questions"),
]

# The marks suffixes the frontend can append. "7-8" is the app's own
# default marks-preference label, so the range form is not a rare case.
MARKS_SUFFIXES = [
    ("", None),
    (", for 8 marks", 8),
    (", for 7-8 marks", 8),
    (", for 10 marks", 10),
]


def test_follow_up_actions() -> None:
    section("6. FOLLOW-UPS - action detected and topic held")

    topic = "Binary Search"

    for phrase, expected_action in FOLLOW_UP_ACTIONS:
        for suffix, expected_marks in MARKS_SUFFIXES:
            query = f"{topic} — {phrase}{suffix}"

            result = _detect_contextual_action(query)

            label = f"{phrase!r}{suffix or ' (no marks)'}"

            if result is None:
                check(
                    f"{label} -> detected",
                    False,
                    "returned None, so the action is silently dropped",
                )
                continue

            actual_topic, actual_action, actual_marks = result

            check(
                f"{label} -> topic stays {topic!r}",
                actual_topic == topic,
                f"got {actual_topic!r}",
            )

            check(
                f"{label} -> action {expected_action!r}",
                actual_action == expected_action,
                f"got {actual_action!r}",
            )

            check(
                f"{label} -> marks {expected_marks}",
                actual_marks == expected_marks,
                f"got {actual_marks}",
            )


def test_follow_ups_never_drift() -> None:
    """The hard requirement: a follow-up must never end up answering
    about COCOMO, SEPM or anything else. This checks the SECOND line of
    defence - even if the contextual bypass were to miss, the topic the
    extractor resolves from the same string must still be Binary Search."""

    section("7. FOLLOW-UPS - no topic drift on the fallback path")

    for phrase, _ in FOLLOW_UP_ACTIONS:
        query = f"Binary Search — {phrase}"

        resolved = TopicExtractor.extract_topic(query)

        check(
            f"{phrase!r} still resolves to 'Binary Search'",
            resolved == "Binary Search",
            f"DRIFTED to {resolved!r}",
        )


def test_follow_up_prompt_holds_topic() -> None:
    section("8. FOLLOW-UP PROMPT - action requirements and topic lock")

    node = {"label": "Binary Search", "type": "Algorithm"}

    for phrase, action in FOLLOW_UP_ACTIONS:
        prompt = PromptBuilder.build_follow_up_prompt(
            topic_name="Binary Search",
            action=action,
            marks=8,
            topic=node,
            outgoing=[],
            incoming=[],
        )

        check(
            f"{action!r} prompt names the topic",
            "Binary Search" in prompt,
        )

        check(
            f"{action!r} prompt forbids changing the topic",
            "NEVER replace the current topic" in prompt,
        )

        check(
            f"{action!r} prompt carries its own action requirements",
            "SAME TOPIC" in prompt,
        )


def test_non_actions_are_ignored() -> None:
    """Anything that is not one of the known action phrases must fall
    through to the normal pipeline rather than being mistaken for one."""

    section("9. NEGATIVE CASES - not contextual actions")

    for query in [
        "Explain Binary Search for 8 marks",       # no em dash
        "Binary Search — what is COCOMO",          # unknown instruction
        "Binary Search - explain it more simply",  # hyphen, not em dash
    ]:
        check(
            f"{query!r} -> not a contextual action",
            _detect_contextual_action(query) is None,
            "was wrongly treated as a contextual action",
        )


# ==============================================================
# 10. EMPTY INPUT
# ==============================================================

def test_empty_input() -> None:
    """An empty or whitespace-only question must be rejected before any
    Neo4j or Ollama work happens. The stub driver above raises if a
    session is opened, so reaching the graph would fail this test."""

    section("10. EMPTY INPUT - rejected before any graph or LLM call")

    from llm.rag_service import RAGService

    for question in ["", "   ", "\n\t "]:
        result = RAGService.answer(question)

        check(
            f"{question!r} -> status False",
            result["status"] is False,
            f"got {result['status']}",
        )

        check(
            f"{question!r} -> no topic, no graph work",
            result["topic"] is None and result["graph_context"] == [],
        )


# ==============================================================
# MAIN
# ==============================================================

def main() -> int:
    print("=" * 68)
    print("EduGraphAI - Phase 5 offline answer-quality verification")
    print("=" * 68)
    print(f"Knowledge Graph labels loaded from CSV : {len(LABELS)}")

    test_normal_questions()
    test_out_of_graph_returns_none()
    test_marks_detection()
    test_eight_mark_structure()
    test_prompt_carries_marks_and_graph()
    test_follow_up_actions()
    test_follow_ups_never_drift()
    test_follow_up_prompt_holds_topic()
    test_non_actions_are_ignored()
    test_empty_input()

    print("\n" + "=" * 68)
    print(f"RESULT: {PASSED} passed, {FAILED} failed")
    print("=" * 68)

    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
