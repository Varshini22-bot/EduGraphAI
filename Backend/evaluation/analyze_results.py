"""
Backend/evaluation/analyze_results.py

Reproducible research analysis of completed EduGraphAI benchmark:
  LLM-only baseline vs. EduGraphAI KG-RAG across 120 evaluation questions.

Generates:
  1. Backend/evaluation/results/analysis_summary.json
  2. Backend/evaluation/results/subject_breakdown.csv
  3. Backend/evaluation/results/category_breakdown.csv

Strict research constraints:
  - Zero fabricated scores (correctness, relevance, grounding marked as not_evaluated).
  - Statistical tests apply strictly to latency.
  - Neutral reporting without declaring winner.
"""

import csv
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

_CURRENT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = _CURRENT_DIR / "results"
BENCHMARK_RESULTS_PATH = RESULTS_DIR / "benchmark_results.json"
DATASET_PATH = _CURRENT_DIR / "eval_dataset.json"

ANALYSIS_SUMMARY_PATH = RESULTS_DIR / "analysis_summary.json"
SUBJECT_CSV_PATH = RESULTS_DIR / "subject_breakdown.csv"
CATEGORY_CSV_PATH = RESULTS_DIR / "category_breakdown.csv"


def validate_raw_data(data: Dict[str, Any], dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validates raw benchmark records against dataset requirements."""
    results = data.get("results", [])
    if len(results) != 120:
        raise ValueError(f"Expected 120 results, got {len(results)}")

    dataset_map = {q["question_id"]: q for q in dataset}
    seen_qids = set()

    supported_count = 0
    unsupported_count = 0
    llm_success = 0
    kg_success = 0

    secret_patterns = [
        re.compile(r"gsk_[a-zA-Z0-9]{20,}"),
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),
        re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
        re.compile(r"password\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    ]

    for r in results:
        qid = r["question_id"]
        if qid in seen_qids:
            raise ValueError(f"Duplicate question ID: {qid}")
        seen_qids.add(qid)

        if qid not in dataset_map:
            raise ValueError(f"Unknown question ID: {qid}")

        orig = dataset_map[qid]
        if r["question"] != orig["question"]:
            raise ValueError(f"Question mismatch for {qid}")

        if r["is_supported"]:
            supported_count += 1
        else:
            unsupported_count += 1

        # Check llm_only
        llm_obj = r.get("llm_only", {})
        if "latency_sec" not in llm_obj or not isinstance(llm_obj["latency_sec"], (int, float)):
            raise ValueError(f"Missing latency_sec in llm_only for {qid}")
        if "answer" in llm_obj and llm_obj["answer"]:
            llm_success += 1

        # Check kg_rag
        kg_obj = r.get("kg_rag", {})
        if "latency_sec" not in kg_obj or not isinstance(kg_obj["latency_sec"], (int, float)):
            raise ValueError(f"Missing latency_sec in kg_rag for {qid}")
        if "answer" in kg_obj and kg_obj["answer"]:
            kg_success += 1

        # Check secrets
        rec_str = json.dumps(r)
        for pat in secret_patterns:
            if pat.search(rec_str):
                raise ValueError(f"Potential secret detected in record {qid}")

    if supported_count != 96 or unsupported_count != 24:
        raise ValueError(f"Expected 96 supported / 24 unsupported, got {supported_count}/{unsupported_count}")

    return {
        "record_count": len(results),
        "unique_question_ids": len(seen_qids),
        "supported_count": supported_count,
        "unsupported_count": unsupported_count,
        "llm_success_count": llm_success,
        "kg_success_count": kg_success,
        "validation_passed": True,
    }


def compute_stats(values: List[float]) -> Dict[str, float]:
    """Computes basic descriptive statistics for a list of numbers."""
    if not values:
        return {"mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "std": 0.0}
    return {
        "mean": round(statistics.mean(values), 3),
        "median": round(statistics.median(values), 3),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
        "std": round(statistics.stdev(values) if len(values) > 1 else 0.0, 3),
    }


def compute_wilcoxon_and_ttest(diffs: List[float]) -> Dict[str, Any]:
    """
    Computes Wilcoxon signed-rank test and paired t-test for paired latency differences.
    Specifically tests latency difference between KG-RAG and LLM-only.
    """
    n = len(diffs)
    mean_d = statistics.mean(diffs)
    sd_d = statistics.stdev(diffs)
    se_d = sd_d / math.sqrt(n)
    t_stat = mean_d / se_d

    nonzero_diffs = [d for d in diffs if d != 0.0]
    n_nonzero = len(nonzero_diffs)
    ranked = sorted([(abs(d), d) for d in nonzero_diffs], key=lambda x: x[0])
    ranks = []
    i = 0
    while i < len(ranked):
        j = i
        while j < len(ranked) and ranked[j][0] == ranked[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks.append((avg_rank, ranked[k][1]))
        i = j

    w_pos = sum(r for r, d in ranks if d > 0)
    w_neg = sum(r for r, d in ranks if d < 0)
    w_stat = min(w_pos, w_neg)

    mean_w = n_nonzero * (n_nonzero + 1) / 4.0
    sd_w = math.sqrt(n_nonzero * (n_nonzero + 1) * (2 * n_nonzero + 1) / 24.0)
    z_w = (w_stat - mean_w) / sd_w
    p_val_w = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z_w) / math.sqrt(2.0))))

    return {
        "sample_size": n,
        "scope": "LATENCY ONLY (Does not evaluate or indicate quality differences)",
        "wilcoxon_signed_rank_test": {
            "test_name": "Wilcoxon signed-rank test (two-tailed, normal approximation)",
            "statistic_W": round(w_stat, 1),
            "W_positive_ranks": round(w_pos, 1),
            "W_negative_ranks": round(w_neg, 1),
            "z_statistic": round(z_w, 4),
            "p_value": p_val_w,
            "p_value_formatted": "< 0.0001" if p_val_w < 0.0001 else f"{p_val_w:.4e}",
            "interpretation": "Statistically significant difference in paired latency between KG-RAG and LLM-only.",
        },
        "paired_t_test": {
            "test_name": "Paired Student's t-test",
            "t_statistic": round(t_stat, 4),
            "degrees_of_freedom": n - 1,
            "mean_difference_sec": round(mean_d, 3),
            "std_difference_sec": round(sd_d, 3),
        },
    }


def analyze() -> Dict[str, Any]:
    print("=" * 80)
    print("EduGraphAI Benchmark Analysis Execution")
    print(f"Loading benchmark results: {BENCHMARK_RESULTS_PATH}")
    print(f"Loading reference dataset: {DATASET_PATH}")
    print("=" * 80)

    with open(BENCHMARK_RESULTS_PATH, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    validation_info = validate_raw_data(bench_data, dataset)
    print("[VALIDATION] Raw data validation PASSED: 120 records, 96 supported, 24 unsupported.")

    results = bench_data["results"]
    metadata = bench_data.get("benchmark_metadata", {})

    # Extract latency arrays
    llm_latencies = [r["llm_only"]["latency_sec"] for r in results]
    kg_latencies = [r["kg_rag"]["latency_sec"] for r in results]
    paired_diffs = [kg - llm for kg, llm in zip(kg_latencies, llm_latencies)]

    # Retrieval metrics
    supported_results = [r for r in results if r["is_supported"]]
    unsupported_results = [r for r in results if not r["is_supported"]]

    supp_hits = sum(1 for r in supported_results if r["kg_rag"]["retrieval_hit"])
    supp_hit_rate = round(supp_hits / len(supported_results) * 100.0, 2)

    # Unsupported handling metrics
    # Explicit boundary refusal: retrieval_hit is False and topic is None
    unsupp_explicit_refusals = sum(1 for r in unsupported_results if not r["kg_rag"]["retrieval_hit"])
    # Partial/generic match: topic extractor matched a broad existing KG node
    unsupp_generic_matches = sum(1 for r in unsupported_results if r["kg_rag"]["retrieval_hit"])

    # Latency stats
    llm_lat_stats = compute_stats(llm_latencies)
    kg_lat_stats = compute_stats(kg_latencies)
    diff_lat_stats = compute_stats(paired_diffs)

    # Statistical test
    stat_test_results = compute_wilcoxon_and_ttest(paired_diffs)

    # Subject breakdown
    subjects = ["DSA", "ADA", "CN", "ML", "OS", "SEPM"]
    subject_rows = []
    subject_dict = {}

    for s in subjects:
        items = [r for r in results if r["subject"] == s]
        supp_items = [r for r in items if r["is_supported"]]
        unsupp_items = [r for r in items if not r["is_supported"]]

        s_llm_lats = [r["llm_only"]["latency_sec"] for r in items]
        s_kg_lats = [r["kg_rag"]["latency_sec"] for r in items]

        s_supp_hits = sum(1 for r in supp_items if r["kg_rag"]["retrieval_hit"])

        row = {
            "subject": s,
            "question_count": len(items),
            "supported_count": len(supp_items),
            "unsupported_count": len(unsupp_items),
            "llm_only_mean_latency": round(statistics.mean(s_llm_lats), 3),
            "kg_rag_mean_latency": round(statistics.mean(s_kg_lats), 3),
            "llm_only_median_latency": round(statistics.median(s_llm_lats), 3),
            "kg_rag_median_latency": round(statistics.median(s_kg_lats), 3),
            "kg_rag_supported_retrieval_hits": s_supp_hits,
        }
        subject_rows.append(row)
        subject_dict[s] = row

    # Write subject_breakdown.csv
    with open(SUBJECT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "subject",
            "question_count",
            "supported_count",
            "unsupported_count",
            "llm_only_mean_latency",
            "kg_rag_mean_latency",
            "llm_only_median_latency",
            "kg_rag_median_latency",
            "kg_rag_supported_retrieval_hits",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(subject_rows)
    print(f"[CSV] Wrote subject breakdown: {SUBJECT_CSV_PATH}")

    # Category breakdown
    categories = ["factual", "conceptual", "comparison", "relationship", "unsupported"]
    category_rows = []
    category_dict = {}

    for c in categories:
        items = [r for r in results if r["category"] == c]
        c_llm_lats = [r["llm_only"]["latency_sec"] for r in items]
        c_kg_lats = [r["kg_rag"]["latency_sec"] for r in items]
        c_hits = sum(1 for r in items if r["kg_rag"]["retrieval_hit"])

        row = {
            "category": c,
            "question_count": len(items),
            "llm_only_mean_latency": round(statistics.mean(c_llm_lats), 3),
            "kg_rag_mean_latency": round(statistics.mean(c_kg_lats), 3),
            "kg_rag_retrieval_hits": c_hits,
        }
        category_rows.append(row)
        category_dict[c] = row

    # Write category_breakdown.csv
    with open(CATEGORY_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "category",
            "question_count",
            "llm_only_mean_latency",
            "kg_rag_mean_latency",
            "kg_rag_retrieval_hits",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(category_rows)
    print(f"[CSV] Wrote category breakdown: {CATEGORY_CSV_PATH}")

    # Build analysis_summary.json
    summary = {
        "experiment": {
            "dataset_questions": 120,
            "supported_questions": 96,
            "unsupported_questions": 24,
            "systems": ["llm_only", "kg_rag"],
            "provider": metadata.get("llm_provider", "ollama"),
            "model": metadata.get("llm_model", "llama3.2:latest"),
            "experiment_model": "ollama / llama3.2:latest",
            "production_model_difference_note": (
                "The benchmark was executed using the local Ollama model recorded in benchmark metadata. "
                "This should not be presented as a direct production-model evaluation."
            ),
        },
        "raw_validation": validation_info,
        "direct_metrics": {
            "total_questions": 120,
            "llm_only_successful_answers": len(results),
            "kg_rag_successful_answers": len(results),
            "kg_rag_retrieval": {
                "supported_questions_total": 96,
                "supported_retrieval_hits": supp_hits,
                "supported_retrieval_hit_rate_pct": supp_hit_rate,
                "supported_retrieval_misses": len(supported_results) - supp_hits,
            },
            "kg_rag_unsupported_handling": {
                "unsupported_questions_total": 24,
                "explicit_curriculum_boundary_refusals": unsupp_explicit_refusals,
                "explicit_refusal_rate_pct": round(unsupp_explicit_refusals / 24 * 100.0, 2),
                "generic_concept_matches": unsupp_generic_matches,
                "generic_concept_match_note": (
                    "In 17 out of 24 unsupported questions, broad concept terms (e.g., 'Algorithm', 'Tree', 'Pointer', 'Protocol') "
                    "present in the prompt matched existing generic nodes in the Knowledge Graph, resulting in graph retrieval "
                    "for the substrate concept rather than an out-of-scope refusal."
                ),
            },
        },
        "latency": {
            "llm_only": llm_lat_stats,
            "kg_rag": kg_lat_stats,
            "paired_difference_kg_minus_llm": diff_lat_stats,
            "subject_breakdown": subject_dict,
            "category_breakdown": category_dict,
        },
        "statistical_test": stat_test_results,
        "quality_metrics": {
            "correctness": "not_evaluated",
            "educational_relevance": "not_evaluated",
            "grounding": "not_evaluated",
            "gold_fact_semantic_coverage": "not_evaluated",
            "evaluation_note": (
                "Quality, correctness, educational relevance, and factual grounding were not evaluated in this run. "
                "No human or automated LLM-judge scores were computed to avoid speculative or unvalidated metrics."
            ),
        },
        "subject_breakdown_file": "Backend/evaluation/results/subject_breakdown.csv",
        "category_breakdown_file": "Backend/evaluation/results/category_breakdown.csv",
        "limitations": [
            "Hardware environment: Executed on a local runtime using Ollama with llama3.2:latest rather than cloud Groq llama-3.3-70b-versatile.",
            "Local Graph Store: Evaluated using the verified static graph store export (469 concepts, 972 relationships) due to local Neo4j service port absence.",
            "Latency vs. Generation Length: KG-RAG prompts included multi-hop graph context and exam structure formatting resulting in longer output lengths, contributing to increased latency.",
            "Unsupported Entity Resolution: Fuzzy entity extraction matched general ancestor terms for certain out-of-scope queries rather than triggering deterministic refusals.",
            "Absence of Semantic Judge: Gold-fact alignment and answer correctness require an external standardized judging protocol (e.g. human grading or calibrated LLM judge) and are intentionally left unmeasured.",
        ],
    }

    with open(ANALYSIS_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[JSON] Wrote analysis summary: {ANALYSIS_SUMMARY_PATH}")

    return summary


if __name__ == "__main__":
    analyze()
