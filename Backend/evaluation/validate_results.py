"""
Backend/evaluation/validate_results.py

Validation script for EduGraphAI research benchmark results.
Verifies that:
1. benchmark_results.json is valid JSON
2. Contains benchmark_metadata and results
3. Exactly 120 result records
4. All 120 question_ids present exactly once
5. All 120 question strings match eval_dataset.json exactly
6. Both systems (llm_only and kg_rag) have a result/error object for every question
7. No API keys, tokens, or secrets occur anywhere in the file
8. No fabricated quality scores exist (correctness, relevance, hallucination, etc.)
9. Dataset metadata (subject, category, is_supported, expected_behavior, gold_facts) matches eval_dataset.json
"""

import json
import re
import sys
from pathlib import Path

_CURRENT_DIR = Path(__file__).resolve().parent
DATASET_PATH = _CURRENT_DIR / "eval_dataset.json"
RESULTS_PATH = _CURRENT_DIR / "results" / "benchmark_results.json"


def validate_results(
    results_path: Path = RESULTS_PATH,
    dataset_path: Path = DATASET_PATH,
) -> bool:
    print(f"Validating benchmark results at: {results_path}")
    if not results_path.exists():
        print(f"FAIL: File does not exist: {results_path}")
        return False

    try:
        with open(results_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            data = json.loads(raw_text)
    except Exception as e:
        print(f"FAIL: Invalid JSON format: {e}")
        return False

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # 1. Check top-level keys
    if "benchmark_metadata" not in data or "results" not in data:
        print("FAIL: Missing 'benchmark_metadata' or 'results' at top level.")
        return False

    metadata = data["benchmark_metadata"]
    results = data["results"]

    # 2. Check metadata
    if metadata.get("dataset_questions") != 120:
        print(f"FAIL: metadata dataset_questions is {metadata.get('dataset_questions')}, expected 120.")
        return False

    if metadata.get("systems") != ["llm_only", "kg_rag"]:
        print(f"FAIL: metadata systems is {metadata.get('systems')}, expected ['llm_only', 'kg_rag'].")
        return False

    # 3. Check record count
    if len(results) != 120:
        print(f"FAIL: Expected exactly 120 results, got {len(results)}.")
        return False

    # Build reference lookup from dataset
    dataset_map = {q["question_id"]: q for q in dataset}
    seen_qids = set()

    # 4. Check forbidden score keys
    forbidden_score_keys = {
        "correctness", "grounding", "relevance", "hallucination",
        "precision", "recall", "f1", "rouge", "bleu", "faithfulness",
        "score", "accuracy"
    }

    # 5. Check secret patterns
    secret_patterns = [
        re.compile(r"gsk_[a-zA-Z0-9]{20,}"),
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),
        re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
        re.compile(r"password\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    ]

    for pat in secret_patterns:
        if pat.search(raw_text):
            print(f"FAIL: Potential secret pattern matched in file: {pat.pattern}")
            return False

    for idx, r in enumerate(results):
        qid = r.get("question_id")
        if not qid:
            print(f"FAIL: Record #{idx} missing question_id.")
            return False

        if qid in seen_qids:
            print(f"FAIL: Duplicate question_id found: {qid}")
            return False
        seen_qids.add(qid)

        if qid not in dataset_map:
            print(f"FAIL: Unknown question_id in results: {qid}")
            return False

        orig = dataset_map[qid]

        # Exact question text check
        if r.get("question") != orig.get("question"):
            print(f"FAIL: Question text mismatch for {qid}.")
            return False

        # Metadata preservation check
        if r.get("subject") != orig.get("subject"):
            print(f"FAIL: Subject mismatch for {qid}.")
            return False

        if r.get("category") != orig.get("category"):
            print(f"FAIL: Category mismatch for {qid}.")
            return False

        if r.get("is_supported") != orig.get("is_supported"):
            print(f"FAIL: is_supported mismatch for {qid}.")
            return False

        if r.get("expected_behavior") != orig.get("expected_behavior"):
            print(f"FAIL: expected_behavior mismatch for {qid}.")
            return False

        orig_gold = orig.get("gold_facts") if "gold_facts" in orig else orig.get("ground_truth_facts", [])
        if r.get("gold_facts") != orig_gold:
            print(f"FAIL: gold_facts mismatch for {qid}.")
            return False

        # Check llm_only object
        llm_obj = r.get("llm_only")
        if not isinstance(llm_obj, dict):
            print(f"FAIL: llm_only is not a dict for {qid}.")
            return False
        if "answer" not in llm_obj and "error" not in llm_obj:
            print(f"FAIL: llm_only missing answer/error for {qid}.")
            return False
        if "latency_sec" not in llm_obj:
            print(f"FAIL: llm_only missing latency_sec for {qid}.")
            return False

        # Check kg_rag object
        kg_obj = r.get("kg_rag")
        if not isinstance(kg_obj, dict):
            print(f"FAIL: kg_rag is not a dict for {qid}.")
            return False
        if "answer" not in kg_obj and "error" not in kg_obj:
            print(f"FAIL: kg_rag missing answer/error for {qid}.")
            return False
        if "latency_sec" not in kg_obj:
            print(f"FAIL: kg_rag missing latency_sec for {qid}.")
            return False

        # Check for forbidden score keys
        for k in r.keys():
            if k.lower() in forbidden_score_keys:
                print(f"FAIL: Forbidden score key found in record {qid}: {k}")
                return False
        for k in llm_obj.keys():
            if k.lower() in forbidden_score_keys:
                print(f"FAIL: Forbidden score key found in llm_only for {qid}: {k}")
                return False
        for k in kg_obj.keys():
            if k.lower() in forbidden_score_keys:
                print(f"FAIL: Forbidden score key found in kg_rag for {qid}: {k}")
                return False

    print("ALL VALIDATION CHECKS PASSED:")
    print(" - Valid JSON")
    print(" - Exactly 120 result records")
    print(" - All 120 question_ids present exactly once")
    print(" - All 120 question strings match eval_dataset.json exactly")
    print(" - Both systems have result/error object for every question")
    print(" - No API keys, tokens, or secrets found")
    print(" - No fabricated scores exist")
    print(" - Dataset metadata is unchanged and preserved")
    return True


if __name__ == "__main__":
    success = validate_results()
    sys.exit(0 if success else 1)
