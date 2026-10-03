"""
Backend/evaluation/run_benchmark.py

Benchmark orchestration script for EduGraphAI research evaluation.
Executes all 120 questions from eval_dataset.json through:
  1. LLM-only baseline (LLMOnlyRunner)
  2. EduGraphAI KG-RAG (KGRAGRunner)

Records raw answers, latency measurements, and retrieved graph context.
Zero fabricated scores. Zero secrets.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure Backend directory is in sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _CURRENT_DIR.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from config import LLM_PROVIDER, LLM_MODEL
from evaluation.baselines.llm_only_runner import LLMOnlyRunner
from evaluation.baselines.kg_rag_runner import KGRAGRunner

# Ensure line-buffered output so background task logs flush in real-time
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass


DATASET_PATH = _CURRENT_DIR / "eval_dataset.json"
RESULTS_DIR = _CURRENT_DIR / "results"
OUTPUT_FILE = RESULTS_DIR / "benchmark_results.json"


def load_dataset(dataset_path: Path) -> List[Dict[str, Any]]:
    """Loads and validates the benchmark evaluation dataset."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"Dataset at {dataset_path} must be a non-empty list.")

    return data


def save_results(output_path: Path, metadata: Dict[str, Any], results: List[Dict[str, Any]]) -> None:
    """Atomically writes benchmark results and metadata to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(".tmp.json")

    payload = {
        "benchmark_metadata": metadata,
        "results": results,
    }

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    temp_path.replace(output_path)


def run_benchmark(
    dataset_path: Path = DATASET_PATH,
    output_path: Path = OUTPUT_FILE,
    resume: bool = True,
    batch_size: int = 0,
) -> Dict[str, Any]:
    """
    Executes the benchmark across all questions in the dataset.
    Supports resuming from checkpoint if previously interrupted.
    batch_size: If > 0, stop after processing this many questions in the current run.
    """
    start_total_time = time.perf_counter()
    dataset = load_dataset(dataset_path)
    total_questions = len(dataset)

    results: List[Dict[str, Any]] = []
    completed_ids = set()

    # Check for existing checkpoint
    if resume and output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_results = existing_data.get("results", [])
            for r in existing_results:
                qid = r.get("question_id")
                if qid:
                    results.append(r)
                    completed_ids.add(qid)
            print(f"[CHECKPOINT] Loaded {len(completed_ids)} previously completed questions from {output_path.name}.")
        except Exception as e:
            print(f"[CHECKPOINT] Could not load existing checkpoint ({e}). Starting fresh.")
            results = []
            completed_ids = set()

    # Initialize runners
    print("=" * 80)
    print(f"EduGraphAI Research Benchmark Orchestration")
    print(f"Total questions in dataset: {total_questions}")
    print(f"Already completed: {len(completed_ids)}")
    print(f"Questions to run: {total_questions - len(completed_ids)}")
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"LLM Model: {LLM_MODEL}")
    print(f"Output path: {output_path}")
    print("=" * 80)

    llm_runner = LLMOnlyRunner()
    kg_runner = KGRAGRunner()

    execution_timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {
        "dataset_questions": total_questions,
        "systems": ["llm_only", "kg_rag"],
        "execution_timestamp": execution_timestamp,
        "llm_provider": LLM_PROVIDER,
        "llm_model": LLM_MODEL,
    }

    llm_success_count = 0
    llm_fail_count = 0
    kg_success_count = 0
    kg_fail_count = 0
    processed_in_this_run = 0

    # Count successes/failures from already completed results
    for r in results:
        llm_obj = r.get("llm_only", {})
        if "error" in llm_obj or not llm_obj.get("answer"):
            llm_fail_count += 1
        else:
            llm_success_count += 1

        kg_obj = r.get("kg_rag", {})
        if "error" in kg_obj or not kg_obj.get("answer"):
            kg_fail_count += 1
        else:
            kg_success_count += 1

    # Iterate through questions
    for idx, q in enumerate(dataset):
        qid = q["question_id"]
        if qid in completed_ids:
            continue

        q_text = q["question"]
        subject = q.get("subject", "")
        category = q.get("category", "")
        is_supported = q.get("is_supported", False)
        expected_behavior = q.get("expected_behavior", "")
        gold_facts = q.get("gold_facts") if "gold_facts" in q else q.get("ground_truth_facts", [])

        print(f"\n[{idx + 1}/{total_questions}] {qid} [{subject} | {category} | sup={is_supported}]: {q_text[:70]}...")

        # ----------------------------------------------------
        # 1. LLM-only Baseline
        # ----------------------------------------------------
        llm_out: Dict[str, Any]
        t0_llm = time.perf_counter()
        try:
            llm_res = llm_runner.run(q_text)
            llm_ans = llm_res.get("answer", "")
            if isinstance(llm_ans, str) and llm_ans.startswith("Error generating answer:"):
                llm_out = {
                    "error": llm_ans,
                    "latency_sec": llm_res.get("latency_sec", round(time.perf_counter() - t0_llm, 3)),
                }
                llm_fail_count += 1
                print(f"  [LLM-only] FAIL (runner error) in {llm_out['latency_sec']}s")
            else:
                llm_out = {
                    "answer": llm_ans,
                    "latency_sec": llm_res.get("latency_sec", round(time.perf_counter() - t0_llm, 3)),
                }
                llm_success_count += 1
                print(f"  [LLM-only] OK ({len(llm_ans)} chars) in {llm_out['latency_sec']}s")
        except Exception as exc:
            llm_lat = round(time.perf_counter() - t0_llm, 3)
            llm_out = {
                "error": str(exc),
                "latency_sec": llm_lat,
            }
            llm_fail_count += 1
            print(f"  [LLM-only] EXCEPTION: {exc} in {llm_lat}s")

        # ----------------------------------------------------
        # 2. EduGraphAI KG-RAG
        # ----------------------------------------------------
        kg_out: Dict[str, Any]
        t0_kg = time.perf_counter()
        try:
            kg_res = kg_runner.run(q_text)
            kg_ans = kg_res.get("answer", "")
            if isinstance(kg_ans, str) and kg_ans.startswith("Error in KG-RAG execution:"):
                kg_out = {
                    "error": kg_ans,
                    "retrieved_context": kg_res.get("retrieved_context", {}),
                    "retrieval_hit": False,
                    "latency_sec": kg_res.get("latency_sec", round(time.perf_counter() - t0_kg, 3)),
                }
                kg_fail_count += 1
                print(f"  [KG-RAG]   FAIL (runner error) in {kg_out['latency_sec']}s")
            else:
                kg_out = {
                    "answer": kg_ans,
                    "retrieved_context": kg_res.get("retrieved_context", {}),
                    "retrieval_hit": kg_res.get("retrieval_hit", False),
                    "latency_sec": kg_res.get("latency_sec", round(time.perf_counter() - t0_kg, 3)),
                }
                kg_success_count += 1
                hit_str = "HIT" if kg_out["retrieval_hit"] else "MISS/FALLBACK"
                print(f"  [KG-RAG]   OK [{hit_str}] ({len(kg_ans)} chars) in {kg_out['latency_sec']}s")
        except Exception as exc:
            kg_lat = round(time.perf_counter() - t0_kg, 3)
            kg_out = {
                "error": str(exc),
                "retrieved_context": {},
                "retrieval_hit": False,
                "latency_sec": kg_lat,
            }
            kg_fail_count += 1
            print(f"  [KG-RAG]   EXCEPTION: {exc} in {kg_lat}s")

        # Assemble question record preserving original dataset fields
        record = {
            "question_id": qid,
            "subject": subject,
            "category": category,
            "is_supported": is_supported,
            "expected_behavior": expected_behavior,
            "gold_facts": gold_facts,
            "question": q_text,
            "llm_only": llm_out,
            "kg_rag": kg_out,
        }

        results.append(record)
        completed_ids.add(qid)
        processed_in_this_run += 1

        # Checkpoint save after every question
        save_results(output_path, metadata, results)

        if batch_size > 0 and processed_in_this_run >= batch_size:
            print(f"\n[BATCH LIMIT REACHED] Processed {processed_in_this_run} questions in this run. Stopping.")
            break

    total_duration = round(time.perf_counter() - start_total_time, 2)

    # Final summary output
    print("\n" + "=" * 80)
    print("BENCHMARK EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total questions attempted : {total_questions}")
    print(f"LLM-only successful       : {llm_success_count}")
    print(f"LLM-only failed           : {llm_fail_count}")
    print(f"KG-RAG successful         : {kg_success_count}")
    print(f"KG-RAG failed             : {kg_fail_count}")
    print(f"Total benchmark duration  : {total_duration} seconds ({round(total_duration / 60, 2)} minutes)")
    print(f"Output path               : {output_path.resolve()}")
    print("=" * 80)

    return {
        "total_attempted": total_questions,
        "llm_success": llm_success_count,
        "llm_failed": llm_fail_count,
        "kg_success": kg_success_count,
        "kg_failed": kg_fail_count,
        "duration_sec": total_duration,
        "output_path": str(output_path.resolve()),
    }


def main():
    parser = argparse.ArgumentParser(description="Run EduGraphAI Research Benchmark.")
    parser.add_argument("--no-resume", action="store_true", help="Do not resume; start fresh.")
    parser.add_argument("--batch-size", type=int, default=0, help="Stop after processing this many questions in this run (0=all).")
    parser.add_argument("--dataset", type=str, default=str(DATASET_PATH), help="Path to evaluation dataset JSON.")
    parser.add_argument("--output", type=str, default=str(OUTPUT_FILE), help="Path to output results JSON.")
    args = parser.parse_args()

    run_benchmark(
        dataset_path=Path(args.dataset),
        output_path=Path(args.output),
        resume=not args.no_resume,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
