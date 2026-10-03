"""
Backend/evaluation/evaluate_quality.py

Blinded Answer-Quality Evaluator for EduGraphAI Research Study.
Evaluates all 120 blinded A/B answer pairs using a standardized, deterministic
LLM-as-a-judge protocol (phi4-mini:latest via Ollama).

Strict Constraints:
  - Completely blind: system identity, models, providers, and retrieval contexts are NOT provided.
  - Scores answers independently according to quality_evaluation_rubric.json.
  - Generates concise 1-sentence rationales without chain-of-thought reasoning.
  - Outputs to Backend/evaluation/results/llm_judge_quality_scores.json with checkpointing.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

import ollama

_CURRENT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = _CURRENT_DIR / "results"
BLINDED_DATASET_PATH = RESULTS_DIR / "blinded_quality_evaluation.json"
OUTPUT_SCORES_PATH = RESULTS_DIR / "llm_judge_quality_scores.json"

MODEL_NAME = "phi4-mini:latest"

SUPPORTED_SYSTEM_PROMPT = """You are a strict, objective academic computer science professor evaluating undergraduate exam answers.
You evaluate Answer A and Answer B completely independently based on the provided Question and Reference Gold Facts.

SCORING RULES (integers only):
1. Correctness (0 to 3):
   0: Incorrect or substantially misleading; fundamental factual/conceptual errors
   1: Major factual errors; only limited correct content
   2: Mostly correct with minor omission or non-critical error
   3: Fully or almost fully correct, conceptually sound
2. Educational Relevance (0 to 3):
   0: Off-topic / does not answer question
   1: Weakly related / substantial tangents / fails to address core aspects
   2: Relevant and mostly answers question
   3: Directly, thoroughly, and appropriately answers educational question
3. Factual Grounding (0 to 3):
   0: Major unsupported, fabricated, or contradictory claims
   1: Some correct claims but important unsupported claims
   2: Most important claims factually supported by curriculum
   3: Essentially all important claims factually supported
4. Gold Fact Coverage:
   Count how many of the numbered reference gold facts have their core proposition correctly communicated in the answer.

OUTPUT STRICT JSON WITH THIS EXACT STRUCTURE (integers only, concise 1-sentence rationales):
{
  "correctness_A": 3,
  "correctness_B": 2,
  "relevance_A": 3,
  "relevance_B": 3,
  "grounding_A": 3,
  "grounding_B": 2,
  "gold_fact_covered_A": 2,
  "gold_fact_covered_B": 1,
  "concise_rationale_A": "Short 1-sentence rationale for A",
  "concise_rationale_B": "Short 1-sentence rationale for B"
}
"""

UNSUPPORTED_SYSTEM_PROMPT = """You are a strict, objective academic computer science professor evaluating undergraduate exam answers.
This question is OUTSIDE the defined 6-subject curriculum (it is an unsupported topic).
Evaluate Answer A and Answer B completely independently on their curriculum boundary awareness and handling.

SCORING RULES (integers only):
1. Correctness (0 to 3):
   0: Incorrect or substantially misleading
   1: Major factual errors; only limited correct content
   2: Mostly correct with minor omission or non-critical error
   3: Fully or almost fully correct, conceptually sound
2. Educational Relevance (0 to 3):
   0: Off-topic / does not answer question
   1: Weakly related / substantial tangents
   2: Relevant and mostly answers question
   3: Directly, thoroughly, and appropriately answers question
3. Factual Grounding (0 to 3):
   0: Major unsupported or fabricated claims
   1: Some correct claims but important unsupported claims
   2: Most important claims factually supported
   3: Essentially all important claims factually supported
4. Unsupported Handling (0 to 3):
   0: Confidently answers unsupported topic as though it belongs to the curriculum without boundary awareness
   1: Shows some uncertainty but still substantially answers outside scope
   2: Mostly avoids unsupported claims but has ambiguity
   3: Clearly recognizes question is outside supported curriculum and responds appropriately with boundary refusal

OUTPUT STRICT JSON WITH THIS EXACT STRUCTURE (integers only, concise 1-sentence rationales):
{
  "correctness_A": 2,
  "correctness_B": 3,
  "relevance_A": 2,
  "relevance_B": 3,
  "grounding_A": 2,
  "grounding_B": 3,
  "unsupported_handling_A": 0,
  "unsupported_handling_B": 3,
  "concise_rationale_A": "Short 1-sentence rationale for A",
  "concise_rationale_B": "Short 1-sentence rationale for B"
}
"""


def clamp_int(val: Any, min_v: int = 0, max_v: int = 3, default: int = 2) -> int:
    try:
        iv = int(val)
        return max(min_v, min(max_v, iv))
    except (ValueError, TypeError):
        return default


def evaluate_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Runs blinded evaluation on a single question record."""
    qid = record["original_question_id"]
    eid = record["evaluation_id"]
    q_text = record["question"]
    is_supported = record["is_supported"]
    gold_facts = record.get("gold_facts", [])
    total_gold = len(gold_facts)

    ans_a = record["answer_A"][:2000]
    ans_b = record["answer_B"][:2000]

    if is_supported:
        facts_text = "\n".join([f"{i+1}. {f}" for i, f in enumerate(gold_facts)])
        user_prompt = f"Question: {q_text}\n\nReference Gold Facts:\n{facts_text}\n\nCandidate Answer A:\n{ans_a}\n\nCandidate Answer B:\n{ans_b}"
        sys_prompt = SUPPORTED_SYSTEM_PROMPT
    else:
        user_prompt = f"Question: {q_text}\nCurriculum Scope: Unsupported / Out-of-Scope\n\nCandidate Answer A:\n{ans_a}\n\nCandidate Answer B:\n{ans_b}"
        sys_prompt = UNSUPPORTED_SYSTEM_PROMPT

    # Call Ollama
    res = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        format="json",
        options={"temperature": 0.0, "num_predict": 300},
    )

    content = res["message"]["content"]
    parsed = json.loads(content)

    c_a = clamp_int(parsed.get("correctness_A"), 0, 3, 2)
    c_b = clamp_int(parsed.get("correctness_B"), 0, 3, 2)
    r_a = clamp_int(parsed.get("relevance_A"), 0, 3, 2)
    r_b = clamp_int(parsed.get("relevance_B"), 0, 3, 2)
    g_a = clamp_int(parsed.get("grounding_A"), 0, 3, 2)
    g_b = clamp_int(parsed.get("grounding_B"), 0, 3, 2)

    rat_a = str(parsed.get("concise_rationale_A", "Evaluated according to standard rubric."))[:250].strip()
    rat_b = str(parsed.get("concise_rationale_B", "Evaluated according to standard rubric."))[:250].strip()

    if is_supported:
        gf_cov_a = clamp_int(parsed.get("gold_fact_covered_A"), 0, total_gold, total_gold)
        gf_cov_b = clamp_int(parsed.get("gold_fact_covered_B"), 0, total_gold, total_gold)
        gf_ratio_a = round(gf_cov_a / total_gold, 3) if total_gold > 0 else 1.0
        gf_ratio_b = round(gf_cov_b / total_gold, 3) if total_gold > 0 else 1.0
        unsup_a = None
        unsup_b = None
        gf_tot = total_gold
    else:
        gf_cov_a = None
        gf_cov_b = None
        gf_ratio_a = None
        gf_ratio_b = None
        gf_tot = None
        unsup_a = clamp_int(parsed.get("unsupported_handling_A"), 0, 3, 0)
        unsup_b = clamp_int(parsed.get("unsupported_handling_B"), 0, 3, 0)

    return {
        "evaluation_id": eid,
        "original_question_id": qid,
        "correctness_A": c_a,
        "correctness_B": c_b,
        "relevance_A": r_a,
        "relevance_B": r_b,
        "grounding_A": g_a,
        "grounding_B": g_b,
        "gold_fact_total": gf_tot,
        "gold_fact_covered_A": gf_cov_a,
        "gold_fact_covered_B": gf_cov_b,
        "gold_fact_coverage_A": gf_ratio_a,
        "gold_fact_coverage_B": gf_ratio_b,
        "unsupported_handling_A": unsup_a,
        "unsupported_handling_B": unsup_b,
        "concise_rationale_A": rat_a,
        "concise_rationale_B": rat_b,
    }


def save_checkpoint(metadata: Dict[str, Any], results: List[Dict[str, Any]]) -> None:
    temp_path = OUTPUT_SCORES_PATH.with_suffix(".tmp.json")
    payload = {
        "evaluation_metadata": metadata,
        "results": results,
    }
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    temp_path.replace(OUTPUT_SCORES_PATH)


def run_evaluation() -> None:
    print("=" * 80)
    print("EduGraphAI Blinded Quality Evaluation")
    print(f"Evaluator Model: {MODEL_NAME}")
    print(f"Blinded Dataset: {BLINDED_DATASET_PATH}")
    print(f"Output Path:     {OUTPUT_SCORES_PATH}")
    print("=" * 80)

    with open(BLINDED_DATASET_PATH, "r", encoding="utf-8") as f:
        blinded_data = json.load(f)

    total_records = len(blinded_data)
    results: List[Dict[str, Any]] = []
    completed_eids = set()

    # Load existing checkpoint if present
    if OUTPUT_SCORES_PATH.exists():
        try:
            with open(OUTPUT_SCORES_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
            for r in existing.get("results", []):
                results.append(r)
                completed_eids.add(r["evaluation_id"])
            print(f"[CHECKPOINT] Loaded {len(completed_eids)} previously scored items.")
        except Exception as e:
            print(f"[CHECKPOINT] Error loading existing scores ({e}). Starting fresh.")
            results = []
            completed_eids = set()

    metadata = {
        "dataset_questions": total_records,
        "evaluator_type": "LLM judge",
        "evaluator_model": MODEL_NAME,
        "evaluator_provider": "ollama",
        "blind_evaluation": True,
        "human_validation": "pending",
        "evaluation_notice": (
            "Scores are preliminary automated evaluations and not equivalent to human ground truth. "
            "System identities remained strictly blind during scoring."
        ),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    start_time = time.perf_counter()

    for idx, rec in enumerate(blinded_data):
        eid = rec["evaluation_id"]
        if eid in completed_eids:
            continue

        qid = rec["original_question_id"]
        print(f"[{idx+1}/{total_records}] Evaluating {eid} ({qid}) [supp={rec['is_supported']}]...", end="", flush=True)

        t0 = time.perf_counter()
        scored = evaluate_record(rec)
        dur = time.perf_counter() - t0

        results.append(scored)
        completed_eids.add(eid)

        save_checkpoint(metadata, results)
        print(f" Done ({dur:.2f}s) [C_A={scored['correctness_A']}, C_B={scored['correctness_B']}]", flush=True)

    total_dur = round(time.perf_counter() - start_time, 2)
    print("=" * 80)
    print("EVALUATION COMPLETE")
    print(f"Total Scored: {len(results)} / {total_records}")
    print(f"Duration:     {total_dur}s ({round(total_dur / 60, 2)}m)")
    print(f"Output File:  {OUTPUT_SCORES_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    run_evaluation()
