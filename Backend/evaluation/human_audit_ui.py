"""
Backend/evaluation/human_audit_ui.py

Local Human Evaluation Interface for EduGraphAI Part 9I-R.
Provides a clean, zero-dependency browser-based interface (and optional CLI)
for the human researcher to personally evaluate all 30 blinded question pairs.

Features:
- 100% Python Standard Library (http.server, json, csv, webbrowser)
- Displays Question, Gold Facts, Answer A, and Answer B strictly blinded
- Enforces Rubric constraints (0-3 scales, valid gold fact coverage bounds)
- Saves progress immediately to Backend/evaluation/results/human_evaluation_template.csv
- Supports Resume, Next, Previous, and Jump to Record
- Never suggests, prefills, or fabricates scores
"""

import argparse
import csv
import json
import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# File Paths
EVAL_DIR = Path(__file__).resolve().parent
RESULTS_DIR = EVAL_DIR / "results"
SAMPLE_PATH = RESULTS_DIR / "human_audit_sample.csv"
RUBRIC_PATH = RESULTS_DIR / "quality_evaluation_rubric.json"
TEMPLATE_PATH = RESULTS_DIR / "human_evaluation_template.csv"

# Load Sample Records & Rubric
def load_data():
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(f"Missing sample file: {SAMPLE_PATH}")
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Missing template file: {TEMPLATE_PATH}")

    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        sample_rows = list(csv.DictReader(f))

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_rows = list(csv.DictReader(f))

    template_map = {r["evaluation_id"]: r for r in template_rows}

    records = []
    for s in sample_rows:
        eid = s["evaluation_id"]
        t = template_map.get(eid, {})
        raw_facts = s["gold_facts"].strip() if s["gold_facts"] else ""
        facts = [f.strip() for f in raw_facts.split(" | ")] if raw_facts else []

        record = {
            "evaluation_id": eid,
            "subject": s["subject"],
            "category": s["category"],
            "question": s["question"],
            "answer_A": s["answer_A"],
            "answer_B": s["answer_B"],
            "gold_facts": facts,
            "gold_fact_total": len(facts) if s["category"] != "unsupported" else 0,
            "correctness_A": t.get("correctness_A", ""),
            "correctness_B": t.get("correctness_B", ""),
            "relevance_A": t.get("relevance_A", ""),
            "relevance_B": t.get("relevance_B", ""),
            "grounding_A": t.get("grounding_A", ""),
            "grounding_B": t.get("grounding_B", ""),
            "gold_fact_covered_A": t.get("gold_fact_covered_A", ""),
            "gold_fact_covered_B": t.get("gold_fact_covered_B", ""),
            "unsupported_handling_A": t.get("unsupported_handling_A", ""),
            "unsupported_handling_B": t.get("unsupported_handling_B", ""),
            "evaluator_notes": t.get("evaluator_notes", "")
        }
        records.append(record)

    rubric = {}
    if RUBRIC_PATH.exists():
        with open(RUBRIC_PATH, "r", encoding="utf-8") as f:
            rubric = json.load(f)

    return records, rubric


def save_single_record(record_update):
    eid = record_update.get("evaluation_id")
    if not eid:
        return False, "Missing evaluation_id"

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_rows = list(csv.DictReader(f))

    fieldnames = [
        "evaluation_id", "subject", "category", "question",
        "answer_A", "answer_B",
        "correctness_A", "correctness_B",
        "relevance_A", "relevance_B",
        "grounding_A", "grounding_B",
        "gold_fact_total", "gold_fact_covered_A", "gold_fact_covered_B",
        "unsupported_handling_A", "unsupported_handling_B",
        "evaluator_notes"
    ]

    updated = False
    for r in template_rows:
        if r["evaluation_id"] == eid:
            for k in [
                "correctness_A", "correctness_B",
                "relevance_A", "relevance_B",
                "grounding_A", "grounding_B",
                "gold_fact_total", "gold_fact_covered_A", "gold_fact_covered_B",
                "unsupported_handling_A", "unsupported_handling_B",
                "evaluator_notes"
            ]:
                if k in record_update:
                    r[k] = str(record_update[k]) if record_update[k] is not None else ""
            updated = True
            break

    if not updated:
        return False, f"Evaluation ID {eid} not found in template."

    with open(TEMPLATE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(template_rows)

    return True, "Saved successfully"


def validate_template_status():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    completed = 0
    errors = []

    for r in rows:
        eid = r["evaluation_id"]
        cat = r["category"]

        # Check basic scores
        basic_ok = all(r[k] != "" for k in [
            "correctness_A", "correctness_B",
            "relevance_A", "relevance_B",
            "grounding_A", "grounding_B"
        ])

        if cat == "unsupported":
            unsupp_ok = r["unsupported_handling_A"] != "" and r["unsupported_handling_B"] != ""
            if basic_ok and unsupp_ok:
                completed += 1
            elif any(r[k] != "" for k in ["correctness_A", "unsupported_handling_A"]):
                errors.append(f"{eid} (unsupported): Incomplete scores")
        else:
            gold_ok = r["gold_fact_covered_A"] != "" and r["gold_fact_covered_B"] != ""
            if basic_ok and gold_ok:
                completed += 1
            elif any(r[k] != "" for k in ["correctness_A", "gold_fact_covered_A"]):
                errors.append(f"{eid} ({cat}): Incomplete scores")

    return {
        "total": total,
        "completed": completed,
        "is_complete": completed == total == 30,
        "errors": errors
    }


# HTML Interface Template
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EduGraphAI — Human Blind Quality Evaluation</title>
<style>
  :root {
    --bg-primary: #0f172a;
    --bg-card: #1e293b;
    --bg-header: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent: #38bdf8;
    --accent-hover: #0284c7;
    --border: #475569;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.5;
    padding: 16px;
  }
  .container { max-width: 1400px; margin: 0 auto; }
  header {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 24px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }
  .title-group h1 { font-size: 1.25rem; color: var(--accent); }
  .title-group p { font-size: 0.85rem; color: var(--text-secondary); }
  .progress-group { display: flex; align-items: center; gap: 16px; }
  .progress-pill {
    background: var(--bg-header);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
  }
  .blind-banner {
    background-color: rgba(245, 158, 11, 0.15);
    border: 1px solid var(--warning);
    color: #fde68a;
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .main-layout { display: grid; grid-template-columns: 1fr 420px; gap: 16px; }
  @media (max-width: 1024px) { .main-layout { grid-template-columns: 1fr; } }
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
  }
  .card-header {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
  }
  .badge {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 4px;
    background: var(--bg-header);
    color: var(--text-primary);
  }
  .badge.subject { background: #1e3a8a; color: #93c5fd; }
  .badge.category { background: #14532d; color: #86efac; }
  .badge.unsupported { background: #7f1d1d; color: #fca5a5; }
  .question-box {
    font-size: 1.05rem;
    font-weight: 600;
    color: #fff;
    margin-bottom: 12px;
  }
  .facts-box {
    background: rgba(15, 23, 42, 0.6);
    border-left: 3px solid var(--accent);
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 0.85rem;
    color: #cbd5e1;
  }
  .facts-box ol { margin-left: 18px; margin-top: 4px; }
  .answers-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }
  @media (max-width: 768px) { .answers-grid { grid-template-columns: 1fr; } }
  .answer-panel {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px;
    height: 480px;
    overflow-y: auto;
  }
  .answer-panel h3 {
    font-size: 0.9rem;
    color: #e2e8f0;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px dashed var(--border);
  }
  .answer-content {
    font-size: 0.85rem;
    color: #cbd5e1;
    white-space: pre-wrap;
    word-break: break-word;
  }
  /* Form Sidebar */
  .form-section {
    position: sticky;
    top: 16px;
    max-height: calc(100vh - 32px);
    overflow-y: auto;
  }
  .form-group { margin-bottom: 14px; }
  .form-group label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 4px;
  }
  .score-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 8px;
  }
  .score-field {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 8px;
  }
  .score-field span { font-size: 0.75rem; color: var(--accent); font-weight: 600; }
  select, input[type="number"], textarea {
    width: 100%;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-primary);
    padding: 6px 8px;
    font-size: 0.85rem;
    margin-top: 4px;
  }
  select:focus, input:focus, textarea:focus {
    outline: none;
    border-color: var(--accent);
  }
  textarea { resize: vertical; min-height: 54px; }
  .btn-row {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: 16px;
  }
  button {
    cursor: pointer;
    background: var(--bg-header);
    border: 1px solid var(--border);
    color: var(--text-primary);
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    transition: background 0.15s;
  }
  button:hover { background: #475569; }
  button.primary {
    background: var(--accent);
    color: #0f172a;
    border-color: var(--accent);
  }
  button.primary:hover { background: var(--accent-hover); }
  .quick-nav {
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    gap: 4px;
    margin-top: 12px;
  }
  .nav-dot {
    text-align: center;
    padding: 4px 0;
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: 4px;
    background: var(--bg-header);
    cursor: pointer;
    border: 1px solid transparent;
  }
  .nav-dot.active { border-color: var(--accent); background: #1e3a8a; }
  .nav-dot.done { background: #065f46; color: #a7f3d0; }
  .rubric-hint {
    font-size: 0.72rem;
    color: var(--text-secondary);
    margin-top: 2px;
  }
  .save-toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: var(--success);
    color: #fff;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.85rem;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
  }
  .save-toast.show { opacity: 1; }
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="title-group">
      <h1>EduGraphAI — Human Blind Quality Evaluation</h1>
      <p>Research Double-Blind Audit (Part 9I-R) • Manual Researcher Entry</p>
    </div>
    <div class="progress-group">
      <span class="progress-pill" id="progressDisplay">Record 1 / 30 • Completed: 0 / 30</span>
      <button id="validateBtn" onclick="runValidation()">Validate 30/30</button>
    </div>
  </header>

  <div class="blind-banner">
    <span>🛡️</span>
    <span><strong>Double-Blind Protocol Active:</strong> Answer A and Answer B are completely randomized and anonymous. Do not attempt to identify or guess the underlying system. Score each answer independently strictly on factual merits and curriculum grounding.</span>
  </div>

  <div class="main-layout">
    <!-- Left Column: Question & Candidate Answers -->
    <div>
      <div class="card">
        <div class="card-header">
          <div>
            <span id="evalIdBadge" style="font-size:1.1rem; color:#38bdf8;">EVAL_001</span>
            <span id="subjectBadge" class="badge subject" style="margin-left:8px;">DSA</span>
            <span id="categoryBadge" class="badge category" style="margin-left:4px;">factual</span>
          </div>
          <span id="statusBadge" class="badge" style="background:#475569;">Unsaved</span>
        </div>

        <div class="question-box" id="questionText">Loading question...</div>

        <div class="facts-box" id="goldFactsContainer">
          <strong>Curriculum Gold Facts (<span id="goldFactsCount">0</span> total):</strong>
          <ol id="goldFactsList"></ol>
        </div>

        <div class="answers-grid">
          <div class="answer-panel">
            <h3>Candidate Stream A</h3>
            <div class="answer-content" id="answerAText">Loading Answer A...</div>
          </div>
          <div class="answer-panel">
            <h3>Candidate Stream B</h3>
            <div class="answer-content" id="answerBText">Loading Answer B...</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Column: Scoring Form -->
    <div class="form-section">
      <div class="card">
        <div class="card-header">
          <span>Manual Quality Scores</span>
          <span style="font-size:0.75rem; color:var(--text-secondary);">Rubric Scale: 0 to 3</span>
        </div>

        <form id="scoreForm" onsubmit="event.preventDefault(); saveCurrent(true);">
          <!-- Correctness -->
          <div class="form-group">
            <label>Correctness (0 = Incorrect, 3 = Fully Correct)</label>
            <div class="score-row">
              <div class="score-field">
                <span>Answer A</span>
                <select id="correctness_A" required>
                  <option value="">--</option>
                  <option value="0">0 - Incorrect</option>
                  <option value="1">1 - Major errors</option>
                  <option value="2">2 - Mostly correct</option>
                  <option value="3">3 - Fully correct</option>
                </select>
              </div>
              <div class="score-field">
                <span>Answer B</span>
                <select id="correctness_B" required>
                  <option value="">--</option>
                  <option value="0">0 - Incorrect</option>
                  <option value="1">1 - Major errors</option>
                  <option value="2">2 - Mostly correct</option>
                  <option value="3">3 - Fully correct</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Relevance -->
          <div class="form-group">
            <label>Educational Relevance (0 = Off-topic, 3 = Direct/Thorough)</label>
            <div class="score-row">
              <div class="score-field">
                <span>Answer A</span>
                <select id="relevance_A" required>
                  <option value="">--</option>
                  <option value="0">0 - Off-topic</option>
                  <option value="1">1 - Weakly related</option>
                  <option value="2">2 - Mostly answers</option>
                  <option value="3">3 - Thorough/Direct</option>
                </select>
              </div>
              <div class="score-field">
                <span>Answer B</span>
                <select id="relevance_B" required>
                  <option value="">--</option>
                  <option value="0">0 - Off-topic</option>
                  <option value="1">1 - Weakly related</option>
                  <option value="2">2 - Mostly answers</option>
                  <option value="3">3 - Thorough/Direct</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Grounding -->
          <div class="form-group">
            <label>Factual Grounding (0 = Fabricated, 3 = Supported)</label>
            <div class="score-row">
              <div class="score-field">
                <span>Answer A</span>
                <select id="grounding_A" required>
                  <option value="">--</option>
                  <option value="0">0 - Unsupported</option>
                  <option value="1">1 - Little grounding</option>
                  <option value="2">2 - Most supported</option>
                  <option value="3">3 - Fully supported</option>
                </select>
              </div>
              <div class="score-field">
                <span>Answer B</span>
                <select id="grounding_B" required>
                  <option value="">--</option>
                  <option value="0">0 - Unsupported</option>
                  <option value="1">1 - Little grounding</option>
                  <option value="2">2 - Most supported</option>
                  <option value="3">3 - Fully supported</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Supported: Gold-Fact Coverage -->
          <div class="form-group" id="goldFactSection">
            <label>Gold-Fact Proposition Coverage (out of <span id="maxFactsLabel">0</span>)</label>
            <div class="score-row">
              <div class="score-field">
                <span>Answer A (Covered)</span>
                <input type="number" id="gold_fact_covered_A" min="0" max="5">
              </div>
              <div class="score-field">
                <span>Answer B (Covered)</span>
                <input type="number" id="gold_fact_covered_B" min="0" max="5">
              </div>
            </div>
            <div class="rubric-hint">Count facts where core proposition is semantically communicated.</div>
          </div>

          <!-- Unsupported: Unsupported Handling -->
          <div class="form-group" id="unsupportedSection" style="display:none;">
            <label>Unsupported Handling (0 = Accepts, 3 = Refuses Boundary)</label>
            <div class="score-row">
              <div class="score-field">
                <span>Answer A</span>
                <select id="unsupported_handling_A">
                  <option value="">--</option>
                  <option value="0">0 - Treats as curriculum</option>
                  <option value="1">1 - Answers with doubt</option>
                  <option value="2">2 - Mostly avoids claims</option>
                  <option value="3">3 - Proper boundary refusal</option>
                </select>
              </div>
              <div class="score-field">
                <span>Answer B</span>
                <select id="unsupported_handling_B">
                  <option value="">--</option>
                  <option value="0">0 - Treats as curriculum</option>
                  <option value="1">1 - Answers with doubt</option>
                  <option value="2">2 - Mostly avoids claims</option>
                  <option value="3">3 - Proper boundary refusal</option>
                </select>
              </div>
            </div>
            <div class="rubric-hint">Score 3 for recognizing curriculum boundary and refusing/redirecting.</div>
          </div>

          <!-- Evaluator Notes -->
          <div class="form-group">
            <label>Evaluator Rationale / Notes (1-3 sentences)</label>
            <textarea id="evaluator_notes" placeholder="e.g. Answer A missed worst-case AVL rotation bound; Answer B covered all gold facts."></textarea>
          </div>

          <!-- Actions -->
          <div class="btn-row">
            <button type="button" onclick="navigate(-1)">← Previous</button>
            <button type="button" onclick="saveCurrent(false)">Save Draft</button>
            <button type="submit" class="primary">Save & Next →</button>
          </div>
        </form>

        <!-- Quick Jump Grid -->
        <div style="margin-top:16px; border-top:1px solid var(--border); padding-top:10px;">
          <div style="font-size:0.75rem; color:var(--text-secondary); margin-bottom:6px;">Quick Jump (1 - 30):</div>
          <div class="quick-nav" id="quickNavGrid"></div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="save-toast" id="toast">Saved successfully!</div>

<script>
let records = [];
let currentIndex = 0;

async function init() {
  const res = await fetch('/api/data');
  const data = await res.json();
  records = data.records;
  
  // Find first uncompleted record or resume at 0
  let firstUnfinished = records.findIndex(r => {
    if (r.category === 'unsupported') {
      return !r.correctness_A || !r.unsupported_handling_A;
    } else {
      return !r.correctness_A || r.gold_fact_covered_A === '';
    }
  });
  
  currentIndex = firstUnfinished >= 0 ? firstUnfinished : 0;
  buildQuickNav();
  renderCurrent();
}

function renderCurrent() {
  const r = records[currentIndex];
  document.getElementById('evalIdBadge').innerText = r.evaluation_id;
  document.getElementById('subjectBadge').innerText = r.subject;
  document.getElementById('categoryBadge').innerText = r.category;
  
  if (r.category === 'unsupported') {
    document.getElementById('categoryBadge').className = 'badge unsupported';
  } else {
    document.getElementById('categoryBadge').className = 'badge category';
  }

  document.getElementById('questionText').innerText = r.question;
  document.getElementById('answerAText').innerText = r.answer_A;
  document.getElementById('answerBText').innerText = r.answer_B;

  // Gold facts container
  const factsCont = document.getElementById('goldFactsContainer');
  const factsList = document.getElementById('goldFactsList');
  const goldSec = document.getElementById('goldFactSection');
  const unsuppSec = document.getElementById('unsupportedSection');

  if (r.category === 'unsupported') {
    factsCont.style.display = 'none';
    goldSec.style.display = 'none';
    unsuppSec.style.display = 'block';
    document.getElementById('gold_fact_covered_A').required = false;
    document.getElementById('gold_fact_covered_B').required = false;
    document.getElementById('unsupported_handling_A').required = true;
    document.getElementById('unsupported_handling_B').required = true;
  } else {
    factsCont.style.display = 'block';
    goldSec.style.display = 'block';
    unsuppSec.style.display = 'none';
    document.getElementById('goldFactsCount').innerText = r.gold_facts.length;
    document.getElementById('maxFactsLabel').innerText = r.gold_facts.length;
    document.getElementById('gold_fact_covered_A').max = r.gold_facts.length;
    document.getElementById('gold_fact_covered_B').max = r.gold_facts.length;
    document.getElementById('gold_fact_covered_A').required = true;
    document.getElementById('gold_fact_covered_B').required = true;
    document.getElementById('unsupported_handling_A').required = false;
    document.getElementById('unsupported_handling_B').required = false;

    factsList.innerHTML = r.gold_facts.map(f => `<li>${f}</li>`).join('');
  }

  // Populate form values
  document.getElementById('correctness_A').value = r.correctness_A !== undefined ? r.correctness_A : '';
  document.getElementById('correctness_B').value = r.correctness_B !== undefined ? r.correctness_B : '';
  document.getElementById('relevance_A').value = r.relevance_A !== undefined ? r.relevance_A : '';
  document.getElementById('relevance_B').value = r.relevance_B !== undefined ? r.relevance_B : '';
  document.getElementById('grounding_A').value = r.grounding_A !== undefined ? r.grounding_A : '';
  document.getElementById('grounding_B').value = r.grounding_B !== undefined ? r.grounding_B : '';
  document.getElementById('gold_fact_covered_A').value = r.gold_fact_covered_A !== undefined ? r.gold_fact_covered_A : '';
  document.getElementById('gold_fact_covered_B').value = r.gold_fact_covered_B !== undefined ? r.gold_fact_covered_B : '';
  document.getElementById('unsupported_handling_A').value = r.unsupported_handling_A !== undefined ? r.unsupported_handling_A : '';
  document.getElementById('unsupported_handling_B').value = r.unsupported_handling_B !== undefined ? r.unsupported_handling_B : '';
  document.getElementById('evaluator_notes').value = r.evaluator_notes || '';

  updateProgress();
  updateNavDots();
}

function updateProgress() {
  const completed = records.filter(r => {
    if (r.category === 'unsupported') {
      return r.correctness_A !== '' && r.unsupported_handling_A !== '';
    } else {
      return r.correctness_A !== '' && r.gold_fact_covered_A !== '';
    }
  }).length;

  document.getElementById('progressDisplay').innerText = `Record ${currentIndex + 1} / 30 • Completed: ${completed} / 30`;
  
  const statusBadge = document.getElementById('statusBadge');
  const curr = records[currentIndex];
  const isDone = curr.category === 'unsupported' ? 
    (curr.correctness_A !== '' && curr.unsupported_handling_A !== '') :
    (curr.correctness_A !== '' && curr.gold_fact_covered_A !== '');
  
  if (isDone) {
    statusBadge.innerText = 'Completed';
    statusBadge.style.background = '#065f46';
    statusBadge.style.color = '#a7f3d0';
  } else {
    statusBadge.innerText = 'Unsaved';
    statusBadge.style.background = '#475569';
    statusBadge.style.color = '#fff';
  }
}

function buildQuickNav() {
  const grid = document.getElementById('quickNavGrid');
  grid.innerHTML = records.map((r, i) => `
    <div class="nav-dot" id="dot-${i}" onclick="jumpTo(${i})">${i + 1}</div>
  `).join('');
}

function updateNavDots() {
  records.forEach((r, i) => {
    const dot = document.getElementById(`dot-${i}`);
    if (!dot) return;
    const isDone = r.category === 'unsupported' ? 
      (r.correctness_A !== '' && r.unsupported_handling_A !== '') :
      (r.correctness_A !== '' && r.gold_fact_covered_A !== '');
    
    dot.className = 'nav-dot' + (i === currentIndex ? ' active' : '') + (isDone ? ' done' : '');
  });
}

async function saveCurrent(advance = false) {
  const r = records[currentIndex];
  const payload = {
    evaluation_id: r.evaluation_id,
    correctness_A: document.getElementById('correctness_A').value,
    correctness_B: document.getElementById('correctness_B').value,
    relevance_A: document.getElementById('relevance_A').value,
    relevance_B: document.getElementById('relevance_B').value,
    grounding_A: document.getElementById('grounding_A').value,
    grounding_B: document.getElementById('grounding_B').value,
    gold_fact_total: r.category !== 'unsupported' ? r.gold_facts.length : '',
    gold_fact_covered_A: r.category !== 'unsupported' ? document.getElementById('gold_fact_covered_A').value : '',
    gold_fact_covered_B: r.category !== 'unsupported' ? document.getElementById('gold_fact_covered_B').value : '',
    unsupported_handling_A: r.category === 'unsupported' ? document.getElementById('unsupported_handling_A').value : '',
    unsupported_handling_B: r.category === 'unsupported' ? document.getElementById('unsupported_handling_B').value : '',
    evaluator_notes: document.getElementById('evaluator_notes').value
  };

  const res = await fetch('/api/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const result = await res.json();
  if (result.success) {
    // Update in-memory record
    Object.assign(r, payload);
    showToast();
    if (advance) {
      if (currentIndex < records.length - 1) {
        currentIndex++;
        renderCurrent();
      } else {
        alert("Completed record 30! Click 'Validate 30/30' at the top to verify full completion.");
        renderCurrent();
      }
    } else {
      renderCurrent();
    }
  } else {
    alert("Error saving: " + result.message);
  }
}

function navigate(direction) {
  const newIdx = currentIndex + direction;
  if (newIdx >= 0 && newIdx < records.length) {
    currentIndex = newIdx;
    renderCurrent();
  }
}

function jumpTo(idx) {
  if (idx >= 0 && idx < records.length) {
    currentIndex = idx;
    renderCurrent();
  }
}

function showToast() {
  const t = document.getElementById('toast');
  t.className = 'save-toast show';
  setTimeout(() => { t.className = 'save-toast'; }, 1800);
}

async function runValidation() {
  const res = await fetch('/api/validate');
  const v = await res.json();
  if (v.is_complete) {
    alert(`🎉 Success! All 30/30 human evaluations are completed and validated.\\nYou can now close this interface and return to the assistant terminal.`);
  } else {
    alert(`Validation Status:\\nCompleted: ${v.completed} / 30\\nPending/Incomplete: ${30 - v.completed}\\n\\nPlease complete all records before finalizing.`);
  }
}

window.onload = init;
</script>
</body>
</html>
"""


class HumanAuditHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif url.path == "/api/data":
            records, rubric = load_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"records": records, "rubric": rubric}).encode("utf-8"))
        elif url.path == "/api/validate":
            status = validate_template_status()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(status).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/save":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                success, msg = save_single_record(data)
                self.send_response(200 if success else 400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Keep terminal log clean
        return


def start_server(port=8505):
    server = None
    for p in range(port, port + 20):
        try:
            server = HTTPServer(("127.0.0.1", p), HumanAuditHandler)
            port = p
            break
        except OSError:
            continue
    if not server:
        print(f"Error: Could not bind to any port between {port} and {port+20}")
        return

    url = f"http://127.0.0.1:{port}"
    print(f"\n========================================================")
    print(f" EduGraphAI — Human Blind Quality Audit Interface")
    print(f"========================================================")
    print(f" Local URL: {url}")
    print(f" Target File: {TEMPLATE_PATH}")
    print(f" Double-blind protocol active. No automated scores used.")
    print(f" Opening web browser automatically...")
    print(f" Press Ctrl+C in this terminal when finished to stop.")
    print(f"========================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAudit server stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EduGraphAI Human Audit UI")
    parser.add_argument("--port", type=int, default=8505, help="Port to run local server on")
    parser.add_argument("--validate", action="store_true", help="Validate current completion status")
    args = parser.parse_args()

    if args.validate:
        status = validate_template_status()
        print(f"Completed: {status['completed']} / {status['total']}")
        print(f"Is 30/30 Complete: {status['is_complete']}")
        if status['errors']:
            print("Issues:", status['errors'])
    else:
        start_server(args.port)
