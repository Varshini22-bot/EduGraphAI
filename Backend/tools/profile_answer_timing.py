"""
profile_answer_timing.py

Measures where time actually goes in the /ask pipeline, on a machine where
Neo4j and Ollama are really running.

WHY THIS EXISTS
---------------
RAGService already prints a per-stage timing summary for every question.
This script drives a fixed set of representative questions through the real
pipeline, parses those summaries, and prints one comparable table - plus two
things the summary does not show on its own:

  * how many Neo4j round trips each question costs (both drivers are
    counted: graph.neo4j_client AND graph.graph_query)
  * the cold-start vs warm-model difference for the LLM

Nothing here is imported by the application. It is a measurement tool.

HOW TO RUN (PowerShell, from the project root)
----------------------------------------------
    cd Backend
    .\venv314\Scripts\Activate.ps1        # or however you activate it
    python tools\profile_answer_timing.py

Neo4j must be running and Ollama must have the model pulled. Add --http to
also measure the HTTP round trip a browser sees (needs uvicorn running).
"""

import argparse
import io
import re
import statistics
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

# Run from anywhere: put Backend/ on the import path.
BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))


# ----------------------------------------------------------------------
# Count Neo4j round trips across BOTH drivers the project uses
# ----------------------------------------------------------------------

QUERY_COUNT = {"n": 0}


def install_query_counter():
    """
    Wraps session.run on both Neo4j entry points so every Cypher statement
    is counted. Read-only instrumentation - it forwards to the real driver
    and returns the real result.
    """

    import graph.neo4j_client as neo4j_client
    import graph.graph_query as graph_query

    def wrap_session(session):
        original_run = session.run

        def counted_run(*args, **kwargs):
            QUERY_COUNT["n"] += 1
            return original_run(*args, **kwargs)

        session.run = counted_run
        return session

    original_get_session = neo4j_client.get_session

    def counted_get_session(*args, **kwargs):
        return wrap_session(original_get_session(*args, **kwargs))

    neo4j_client.get_session = counted_get_session

    # graph_query exposes a module-level driver; wrap the sessions it makes.
    original_driver_session = graph_query.driver.session

    def counted_driver_session(*args, **kwargs):
        return wrap_session(original_driver_session(*args, **kwargs))

    graph_query.driver.session = counted_driver_session


# ----------------------------------------------------------------------
# Parse the timing summary RAGService already prints
# ----------------------------------------------------------------------

# Parse the [TIMING] lines rather than the "RAG PERFORMANCE SUMMARY" block,
# because only the [TIMING] lines are printed on BOTH code paths. The
# contextual-action bypass (used by follow-up questions) returns before the
# summary block is ever reached, so a summary-only parser would silently
# report zeros for exactly the follow-up case we most want to measure.
TIMING_LINE = re.compile(r"\[TIMING\]\s*(.+?)\s*:\s*([0-9.]+)\s*seconds?")

# Both wordings of each stage map onto one column. The follow-up path names
# its prompt stage differently and reports "TOTAL REQUEST" where the full
# path reports "Total request time".
STAGE_ALIASES = {
    "topic extraction": "topic",
    "graph retrieval": "graph",
    "prompt construction": "prompt",
    "follow-up prompt construction": "prompt",
    "ollama generation": "llm",
    "learning path": "path",
    "recommendations": "recs",
    "total request": "total",
    "total request time": "total",
}


def parse_stages(text):
    """
    Returns {column: seconds}. A missing stage means that stage genuinely
    did not run - notably 'topic' is absent for follow-up questions, which
    is the contextual bypass working as intended, not a parse failure.
    """

    found = {}
    for line in text.splitlines():
        match = TIMING_LINE.search(line)
        if match:
            column = STAGE_ALIASES.get(match.group(1).strip().lower())
            if column:
                found[column] = float(match.group(2))
    return found


# ----------------------------------------------------------------------
# Representative questions - one per subject, plus a follow-up
# ----------------------------------------------------------------------

QUESTIONS = [
    ("ADA  8-mark", "Explain Binary Search for 8 marks"),
    ("ADA  follow-up", "Binary Search - explain it more simply, for 8 marks"),
    ("DSA  compare", "Compare BFS and DFS"),
    ("ML   default", "Explain Machine Learning"),
    ("CN   default", "Explain the OSI model"),
    ("OS   default", "Explain Deadlock"),
    ("SEPM 10-mark", "Give a 10-mark answer for Software Testing"),
    ("verbose phrasing", "Can you please tell me about Merge Sort in detail for 8 marks"),
]


def run_question(RAGService, question):
    """
    Runs one question, swallowing the pipeline's own console output so the
    table stays readable. Returns (stages, queries, wall_clock, result).
    """

    QUERY_COUNT["n"] = 0
    buffer = io.StringIO()
    start = time.perf_counter()

    with redirect_stdout(buffer):
        result = RAGService.answer(question)

    wall = time.perf_counter() - start
    return parse_stages(buffer.getvalue()), QUERY_COUNT["n"], wall, result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--http",
        metavar="BASE_URL",
        nargs="?",
        const="http://127.0.0.1:8000",
        help="also time GET /ask over HTTP (needs uvicorn running)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="times to run each question (>1 shows warm-model timings)",
    )
    args = parser.parse_args()

    install_query_counter()
    from llm.rag_service import RAGService

    print("=" * 100)
    print("ANSWER-FETCHING PIPELINE TIMINGS")
    print("=" * 100)

    header = (
        f"{'question':22s} {'resolved topic':26s} {'qry':>4s} "
        f"{'extract':>7s} {'graph':>7s} {'prompt':>7s} "
        f"{'LLM':>8s} {'path':>7s} {'recs':>7s} {'TOTAL':>8s}"
    )
    print(header)
    print("-" * len(header))

    totals = []
    llms = []
    queries = []

    for label, question in QUESTIONS:
        for run_index in range(args.repeat):
            stages, count, wall, result = run_question(RAGService, question)

            topic = str(result.get("topic"))[:26]
            total = stages.get("total", wall)
            llm = stages.get("llm", 0.0)

            totals.append(total)
            llms.append(llm)
            queries.append(count)

            tag = label if run_index == 0 else f"  (repeat {run_index + 1})"

            def cell(key):
                # "-" distinguishes "this stage did not run" (follow-up
                # questions skip topic extraction) from "it ran in 0.00s".
                return f"{stages[key]:7.2f}" if key in stages else f"{'-':>7s}"

            print(
                f"{tag:22s} {topic:26s} {count:4d} "
                f"{cell('topic')} "
                f"{cell('graph')} "
                f"{cell('prompt')} "
                f"{llm:8.2f} "
                f"{cell('path')} "
                f"{cell('recs')} "
                f"{total:8.2f}"
            )

    print("-" * 100)
    print(
        f"{'MEAN':22s} {'':26s} {statistics.mean(queries):4.1f} "
        f"{'':7s} {'':7s} {'':7s} "
        f"{statistics.mean(llms):8.2f} {'':7s} {'':7s} "
        f"{statistics.mean(totals):8.2f}"
    )

    if totals:
        share = 100.0 * statistics.mean(llms) / statistics.mean(totals)
        print(f"\nOllama generation is {share:.1f}% of mean total request time.")
        print(
            "Everything else (topic extraction, Neo4j retrieval, prompt "
            "construction,\nlearning path, recommendations) shares the "
            f"remaining {100 - share:.1f}%."
        )

    # ------------------------------------------------------------------
    # Optional: what the browser actually waits for
    # ------------------------------------------------------------------

    if args.http:
        import json
        import urllib.parse
        import urllib.request

        print("\n" + "=" * 100)
        print(f"HTTP ROUND TRIP  ({args.http})")
        print("=" * 100)

        for label, question in QUESTIONS[:3]:
            ask_url = (
                f"{args.http}/ask?query="
                + urllib.parse.quote(question)
            )

            start = time.perf_counter()
            with urllib.request.urlopen(ask_url, timeout=600) as response:
                payload = json.loads(response.read().decode("utf-8"))
            ask_time = time.perf_counter() - start

            topic = payload.get("topic")

            # The second request the UI used to make after every answer.
            # It is no longer part of the ask flow - timed here only to
            # show what was removed.
            graph_time = None
            if topic:
                graph_url = (
                    f"{args.http}/graph/topic/"
                    + urllib.parse.quote(str(topic))
                )
                start = time.perf_counter()
                try:
                    with urllib.request.urlopen(graph_url, timeout=120) as response:
                        response.read()
                    graph_time = time.perf_counter() - start
                except Exception as error:
                    print(f"  (graph request failed: {error})")

            print(f"\n{label}: {question}")
            print(f"  GET /ask                     : {ask_time:7.2f} sec")
            if graph_time is not None:
                print(f"  GET /graph/topic (no longer  : {graph_time:7.2f} sec")
                print(f"   issued by the UI)")
                print(
                    f"  old total the browser waited : "
                    f"{ask_time + graph_time:7.2f} sec"
                )
                print(f"  new total the browser waits  : {ask_time:7.2f} sec")

    print("\nDone.")


if __name__ == "__main__":
    main()
