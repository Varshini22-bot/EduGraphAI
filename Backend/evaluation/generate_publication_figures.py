"""
EduGraphAI — Part 11A: Publication-Ready Research Figures Generator
Produces 4 high-resolution (>= 300 DPI) academic figures using Matplotlib.

Strictly grounded in Part 9K validated statistics:
- Figure 1: EduGraphAI System Architecture & Knowledge Graph Retrieval Workflow
- Figure 2: Comprehensive Evaluation Pipeline & Double-Blind Audit Architecture
- Figure 3: Validated Double-Blind Human Evaluation Scores (95% Bootstrap CIs)
- Figure 4: Local Benchmark Latency Comparison (Ollama llama3.2:latest, N = 120)

Mandatory labeling:
"Source: EduGraphAI Part 9K validated evaluation"
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "evaluation" / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
STATISTICS_PATH = RESULTS_DIR / "part_9k_validated_statistics.json"
BENCHMARK_RESULTS_PATH = RESULTS_DIR / "benchmark_results.json"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def set_academic_style():
    """Configure matplotlib for publication-quality figures."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.5,
        "axes.labelweight": "medium",
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "figure.titlesize": 12,
        "figure.titleweight": "bold",
        "axes.edgecolor": "#2D3748",
        "axes.linewidth": 1.0,
        "grid.color": "#CBD5E0",
        "grid.alpha": 0.35,
        "grid.linestyle": "--",
    })


def generate_figure_1():
    """FIGURE 1: EduGraphAI System Architecture & Knowledge Graph Retrieval Workflow"""
    fig, ax = plt.subplots(figsize=(14.5, 7.6), dpi=300)
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 7.6)
    ax.axis("off")

    c_widths = 2.25
    gap = 0.50
    x_start = 0.45
    xs = [x_start + i * (c_widths + gap) for i in range(5)]

    stages = [
        (xs[0], 0.8, c_widths, 6.0, "1. Presentation Layer", "#EBF3FB", "#2B6CB0"),
        (xs[1], 0.8, c_widths, 6.0, "2. Query Processing", "#F0F4F8", "#334E68"),
        (xs[2], 0.8, c_widths, 6.0, "3. Knowledge Graph Engine", "#E6F4EA", "#22543D"),
        (xs[3], 0.8, c_widths, 6.0, "4. Grounded Inference", "#FEF7E0", "#B06000"),
        (xs[4], 0.8, c_widths, 6.0, "5. Educational Delivery", "#F3E8FD", "#6B46C1"),
    ]

    for x, y, w, h, title, bg, border in stages:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, linewidth=1.5, alpha=0.9)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top",
                fontsize=9.2, fontweight="bold", color=border)

    w_node = 1.90
    x_offsets = [x + (c_widths - w_node) / 2 for x in xs]

    nodes = [
        # Stage 1: Presentation
        (x_offsets[0], 5.3, w_node, 0.9, "Student / Evaluator\n• Question Input\n• Mark Budget (2/5/10)", "#FFFFFF", "#2B6CB0"),
        (x_offsets[0], 4.0, w_node, 1.0, "Next.js 14 Frontend UI\n• React & Tailwind CSS\n• Markdown Formatter", "#FFFFFF", "#2B6CB0"),
        (x_offsets[0], 1.1, w_node, 2.5, "Interactive Learning Canvas\n• Force-Directed Concept Graph\n• Step-by-Step Marking Pills\n• Directed Learning Pathways\n• Next-Topic Knowledge Chips", "#FFFFFF", "#2B6CB0"),

        # Stage 2: Query Processing
        (x_offsets[1], 4.5, w_node, 1.7, "FastAPI REST Gateway\n• /api/query & /api/graph\n• Intent Classification\n• Target Subject Scope", "#FFFFFF", "#334E68"),
        (x_offsets[1], 2.8, w_node, 1.4, "Entity Normalization\n• Topic & Entity Extraction\n• Lemmatization & Alias Map\n• Canonical Concept IDs", "#FFFFFF", "#334E68"),
        (x_offsets[1], 1.1, w_node, 1.4, "Scope Validation\n• Syllabus Coverage Check\n• Out-of-Scope Detection\n• Fallback Refusal Trigger", "#FFFFFF", "#334E68"),

        # Stage 3: Knowledge Graph Engine
        (x_offsets[2], 4.7, w_node, 1.5, "Neo4j Graph Database\n• AuraDB Cloud / Bolt Local\n• 6 CS Subject Ontologies\n• 458 Concept Entities", "#FFFFFF", "#22543D"),
        (x_offsets[2], 2.9, w_node, 1.5, "Multi-Hop Cypher Engine\n• Directed Edge Traversal\n• IS_A, USES, PART_OF\n• Prerequisite Discovery", "#FFFFFF", "#22543D"),
        (x_offsets[2], 1.1, w_node, 1.5, "Subgraph Extraction\n• 1-to-2 Hop Neighborhood\n• Triples Linearization\n• Context Subgraph JSON", "#FFFFFF", "#22543D"),

        # Stage 4: Grounded Inference
        (x_offsets[3], 4.7, w_node, 1.5, "Dual LLM Engine\n• Local: Ollama llama3.2 (3B)\n• Cloud: Groq llama-3.3 (70B)\n• Deterministic Seed (42)", "#FFFFFF", "#B06000"),
        (x_offsets[3], 2.9, w_node, 1.5, "Prompt Construction\n• Syllabus Constraints\n• Marking Scheme Rubric\n• Context Triples Injection", "#FFFFFF", "#B06000"),
        (x_offsets[3], 1.1, w_node, 1.5, "Grounded Generation\n• Strict Context Synthesis\n• Refusal on Zero-Context\n• Hallucination Reduction", "#FFFFFF", "#B06000"),

        # Stage 5: Educational Delivery
        (x_offsets[4], 5.15, w_node, 0.95, "Structured Answer\n• Definitions & Concepts\n• Formulae & Code Examples", "#FFFFFF", "#6B46C1"),
        (x_offsets[4], 3.85, w_node, 0.95, "Marking Breakdown\n• Point-by-Point Rubric\n• Step-Wise Marks Pill", "#FFFFFF", "#6B46C1"),
        (x_offsets[4], 2.55, w_node, 0.95, "Syllabus Guardrails\n• Out-of-Scope Alert\n• Topic Redirection", "#FFFFFF", "#6B46C1"),
        (x_offsets[4], 1.1, w_node, 1.15, "Pedagogical Subgraphs\n• D3.js Rendered Graph\n• Learning Pathways\n• Next-Topic Chips", "#FFFFFF", "#6B46C1"),
    ]

    for x, y, w, h, text, bg, border in nodes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.1",
                             facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=7.8, color="#1A202C")

    def draw_arrow(p1, p2, label="", color="#2D3748", label_side="top", fontsize=7.2):
        arrow = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                                color=color, linewidth=1.3)
        ax.add_patch(arrow)
        if label:
            if label_side == "top":
                mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 0.08)
                ax.text(mid[0], mid[1], label, ha="center", va="bottom", fontsize=fontsize,
                        fontweight="bold", color=color)
            elif label_side == "right":
                mid = ((p1[0] + p2[0]) / 2 + 0.06, (p1[1] + p2[1]) / 2)
                ax.text(mid[0], mid[1], label, ha="left", va="center", fontsize=fontsize,
                        fontweight="bold", color=color)

    # Internal Stage 1
    draw_arrow((x_offsets[0] + w_node / 2, 5.3), (x_offsets[0] + w_node / 2, 5.0), label="Query", label_side="right")

    # Internal Stage 2
    draw_arrow((x_offsets[1] + w_node / 2, 4.5), (x_offsets[1] + w_node / 2, 4.2), label="Analyze", label_side="right")
    draw_arrow((x_offsets[1] + w_node / 2, 2.8), (x_offsets[1] + w_node / 2, 2.5), label="Verify", label_side="right")

    # Internal Stage 3
    draw_arrow((x_offsets[2] + w_node / 2, 4.7), (x_offsets[2] + w_node / 2, 4.4), label="Query", label_side="right")
    draw_arrow((x_offsets[2] + w_node / 2, 2.9), (x_offsets[2] + w_node / 2, 2.6), label="Extract", label_side="right")

    # Internal Stage 4
    draw_arrow((x_offsets[3] + w_node / 2, 4.7), (x_offsets[3] + w_node / 2, 4.4), label="Select", label_side="right")
    draw_arrow((x_offsets[3] + w_node / 2, 2.9), (x_offsets[3] + w_node / 2, 2.6), label="Inject", label_side="right")

    # Inter-Stage Forward Flow
    # 1 -> 2: Next.js to REST Gateway
    draw_arrow((x_offsets[0] + w_node, 4.5), (x_offsets[1], 4.5), label="REST POST", color="#2B6CB0")

    # 2 -> 3: Entity Normalization to Cypher Engine
    draw_arrow((x_offsets[1] + w_node, 3.5), (x_offsets[2], 3.5), label="Cypher Match", color="#334E68")

    # 3 -> 4: Subgraph Extraction to Prompt Construction
    draw_arrow((x_offsets[2] + w_node, 3.5), (x_offsets[3], 3.5), label="Triples Subgraph", color="#22543D")

    # 4 -> 5: Grounded Generation to Output Components
    draw_arrow((x_offsets[3] + w_node, 1.8), (x_offsets[4], 1.8), label="JSON Package", color="#B06000")

    # Return Loop to Interactive Canvas
    ret_arrow = FancyArrowPatch((x_offsets[4], 1.2), (x_offsets[0] + w_node, 1.2),
                                arrowstyle="-|>", mutation_scale=12,
                                color="#2B6CB0", linewidth=1.5,
                                connectionstyle="arc3,rad=-0.14")
    ax.add_patch(ret_arrow)
    ax.text(7.25, 0.32, "Delivered Response (Answer + Marking Scheme + Subgraph Payload)",
            ha="center", va="bottom", fontsize=8, fontweight="bold", color="#2B6CB0")

    # Title & Metadata
    ax.text(7.25, 7.25, "Figure 1: EduGraphAI System Architecture & Knowledge Graph Retrieval Workflow",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#1A365D")
    ax.text(14.1, 0.12, "Source: EduGraphAI Architecture Specification",
            ha="right", va="bottom", fontsize=7.5, fontstyle="italic", color="#718096")

    output_path = FIGURES_DIR / "Figure_1_EduGraphAI_Architecture.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated Figure 1: {output_path}")


def generate_figure_2():
    """FIGURE 2: Evaluation Pipeline (120-Question Benchmark vs 30-Question Human Audit)"""
    fig, ax = plt.subplots(figsize=(13.2, 7.6), dpi=300)
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 7.6)
    ax.axis("off")

    # Background Sections
    # Section A: Full Benchmark (Left)
    box_full = FancyBboxPatch((0.4, 0.4), 5.9, 6.4, boxstyle="round,pad=0.1,rounding_size=0.15",
                              facecolor="#F7FAFC", edgecolor="#CBD5E0", linewidth=1.5)
    ax.add_patch(box_full)
    ax.text(3.35, 6.55, "Full Benchmark Evaluation (N = 120 Questions)",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="#2D3748")

    # Section B: Stratified Human Audit (Right)
    box_human = FancyBboxPatch((6.7, 0.4), 6.1, 6.4, boxstyle="round,pad=0.1,rounding_size=0.15",
                               facecolor="#F0FFF4", edgecolor="#38A169", linewidth=2.0)
    ax.add_patch(box_human)
    ax.text(9.75, 6.55, "Double-Blind Human Quality Audit (N = 30 Sample)",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="#22543D")

    # Nodes in Full Benchmark
    fnodes = [
        (0.7, 4.9, 5.3, 1.25, "Standardized Evaluation Dataset (N = 120)\n• 6 Subjects: ADA, CN, DSA, ML, OS, SEPM (20 each)\n• 5 Categories: Factual (24), Conceptual (24), Comparison (24),\n  Relationship (24), Unsupported (24)", "#FFFFFF", "#4A5568"),
        (0.7, 3.3, 2.5, 1.1, "LLM-Only Baseline\n• Ollama llama3.2 (3B)\n• Zero graph context\n• Direct prompt", "#FFFFFF", "#3182CE"),
        (3.5, 3.3, 2.5, 1.1, "EduGraphAI KG-RAG\n• Ollama llama3.2 (3B)\n• Neo4j graph context\n• Multi-hop Cypher", "#FFFFFF", "#2F855A"),
        (0.7, 1.9, 5.3, 0.95, "120 Paired Generation Outputs (240 Answers Total)\n• End-to-End Latency Logging (120 Pairs)\n• Baseline: 20.19 s vs. KG-RAG: 47.29 s (2.34× factor)", "#FFFFFF", "#805AD5"),
        (0.7, 0.65, 5.3, 0.85, "Automated LLM Judge Evaluation (phi4-mini via Ollama)\n• Evaluated 120 pairs (Demonstrated leniency bias: +0.38 to +0.65)", "#FFFFFF", "#718096"),
    ]

    for x, y, w, h, text, bg, border in fnodes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.1",
                             facecolor=bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8, color="#1A202C")

    # Nodes in Human Audit
    hnodes = [
        (7.0, 4.9, 5.5, 1.25, "Stratified Representative Sampling (N = 30 Pairs)\n• 5 Questions per Subject (24 Supported + 6 Unsupported)\n• Answer A / Answer B Order Randomization\n• Double-Blind Presentation (System IDs Cryptographically Hidden)", "#FFFFFF", "#2F855A"),
        (7.0, 3.45, 5.5, 1.05, "Independent Human Scoring (Pre-Registered Rubric)\n• Correctness (0–3)  • Educational Relevance (0–3)\n• Factual Grounding (0–3)  • Gold-Fact Coverage (24 supported)\n• Unsupported Handling (6 out-of-scope)", "#FFFFFF", "#2B6CB0"),
        (7.0, 2.05, 5.5, 1.05, "Secure Unblinding & Non-Parametric Hypothesis Testing\n• SciPy 1.18.1 Paired Two-Sided Wilcoxon Signed-Rank Test\n• Holm-Bonferroni Step-Down Multiplicity Correction (α = 0.05)\n• Percentile Bootstrap Confidence Intervals (B = 10,000, seed = 42)\n• Paired Effect Sizes (Cohen's dz)", "#FFFFFF", "#C53030"),
        (7.0, 0.65, 5.5, 1.05, "Final Validated Research Findings\n• Correctness: LLM-Only higher (p = 0.0088, significant)\n• Relevance (p = 0.25) & Grounding (p = 0.079): Not significant\n• Unsupported Refusal: Directional advantage (dz = +0.85, exploratory)", "#FFFFFF", "#22543D"),
    ]

    for x, y, w, h, text, bg, border in hnodes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.1",
                             facecolor=bg, edgecolor=border, linewidth=1.3)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8, color="#1A202C")

    # Connectors
    def draw_parrow(p1, p2, color="#4A5568", style="-|>"):
        arrow = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=10,
                                color=color, linewidth=1.3)
        ax.add_patch(arrow)

    draw_parrow((1.95, 4.9), (1.95, 4.4))
    draw_parrow((4.75, 4.9), (4.75, 4.4))
    draw_parrow((1.95, 3.3), (2.55, 2.85))
    draw_parrow((4.75, 3.3), (4.15, 2.85))
    draw_parrow((3.35, 1.9), (3.35, 1.5))

    # Stratified Sample Bridge Arrow
    bridge = FancyArrowPatch((6.0, 5.5), (7.0, 5.5), arrowstyle="-|>", mutation_scale=14,
                             color="#38A169", linewidth=2.5)
    ax.add_patch(bridge)
    ax.text(6.5, 5.7, "Stratified\nSampling", ha="center", va="bottom",
            fontsize=8, fontweight="bold", color="#22543D")

    draw_parrow((9.75, 4.9), (9.75, 4.5))
    draw_parrow((9.75, 3.45), (9.75, 3.1))
    draw_parrow((9.75, 2.05), (9.75, 1.7))

    # Title & Metadata
    ax.text(6.6, 7.25, "Figure 2: Comprehensive Evaluation Pipeline & Double-Blind Audit Architecture",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#1A365D")
    ax.text(12.8, 0.12, "Source: EduGraphAI Part 9K validated evaluation",
            ha="right", va="bottom", fontsize=7.5, fontstyle="italic", color="#718096")

    output_path = FIGURES_DIR / "Figure_2_Evaluation_Pipeline.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated Figure 2: {output_path}")


def generate_figure_3():
    """FIGURE 3: Human Evaluation Scores (Validated Part 9K Results)"""
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.4), dpi=300, gridspec_kw={"width_ratios": [3.2, 1.2, 1.5]})

    # Palette
    c_kg = "#2B6CB0"    # Deep Blue
    c_llm = "#718096"   # Slate Gray

    # -------------------------------------------------------------
    # Panel A: Primary Quality Metrics (N=30, 0-3 scale)
    # -------------------------------------------------------------
    ax1 = axes[0]
    metrics_a = ["Correctness", "Educational Relevance", "Factual Grounding"]
    x_a = np.arange(len(metrics_a))
    w = 0.32

    # Validated Part 9K means
    kg_means_a = [2.133, 2.167, 2.167]
    llm_means_a = [2.600, 2.367, 2.400]

    # Empirical Bootstrap 95% CIs for individual group means:
    # Correctness: KG [1.833, 2.400], LLM [2.333, 2.800]
    # Relevance: KG [1.900, 2.400], LLM [2.133, 2.567]
    # Grounding: KG [1.867, 2.433], LLM [2.100, 2.667]
    kg_err_a = [
        [2.133 - 1.833, 2.167 - 1.900, 2.167 - 1.867],  # lower err
        [2.400 - 2.133, 2.400 - 2.167, 2.433 - 2.167],  # upper err
    ]
    llm_err_a = [
        [2.600 - 2.333, 2.367 - 2.133, 2.400 - 2.100],  # lower err
        [2.800 - 2.600, 2.567 - 2.367, 2.667 - 2.400],  # upper err
    ]

    rects1 = ax1.bar(x_a - w/2, kg_means_a, w, yerr=kg_err_a, capsize=4,
                     label="EduGraphAI KG-RAG", color=c_kg, edgecolor="#1A365D", linewidth=1.1)
    rects2 = ax1.bar(x_a + w/2, llm_means_a, w, yerr=llm_err_a, capsize=4,
                     label="LLM-Only Baseline", color=c_llm, edgecolor="#2D3748", linewidth=1.1)

    # Values cleanly placed above upper error bar caps (upper cap + 0.08)
    kg_caps_a = [2.400, 2.400, 2.433]
    llm_caps_a = [2.800, 2.567, 2.667]
    for r, cap, val in zip(rects1, kg_caps_a, kg_means_a):
        ax1.text(r.get_x() + r.get_width()/2, cap + 0.08, f"{val:.3f}",
                 ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=c_kg)
    for r, cap, val in zip(rects2, llm_caps_a, llm_means_a):
        ax1.text(r.get_x() + r.get_width()/2, cap + 0.08, f"{val:.3f}",
                 ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#2D3748")

    # Statistical significance brackets
    # Correctness: Holm p = 0.00875 (Significant)
    ax1.plot([x_a[0]-w/2, x_a[0]-w/2, x_a[0]+w/2, x_a[0]+w/2], [3.05, 3.12, 3.12, 3.05], color="#C53030", lw=1.2)
    ax1.text(x_a[0], 3.14, "p = 0.0088**\n(Holm adj.)", ha="center", va="bottom", fontsize=7.5, color="#C53030", fontweight="bold")

    # Relevance: Holm p = 0.25 (n.s.)
    ax1.text(x_a[1], 2.85, "p = 0.25 (n.s.)", ha="center", va="bottom", fontsize=7.5, color="#718096")

    # Grounding: Holm p = 0.0785 (n.s. after Holm)
    ax1.text(x_a[2], 2.95, "p = 0.079 (n.s.)\n(Holm adj.)", ha="center", va="bottom", fontsize=7.5, color="#718096")

    ax1.set_ylabel("Mean Human Score (0–3 Scale)")
    ax1.set_ylim(0, 3.45)
    ax1.set_xticks(x_a)
    ax1.set_xticklabels(metrics_a, rotation=10, ha="right")
    ax1.set_title("(A) Primary Quality Metrics (n = 30)", loc="left", fontsize=10)
    ax1.legend(loc="lower left", framealpha=0.9)

    # -------------------------------------------------------------
    # Panel B: Unsupported Handling (n=6, 0-3 scale, exploratory)
    # -------------------------------------------------------------
    ax2 = axes[1]
    metrics_b = ["Unsupported\nHandling"]
    x_b = np.array([0])

    kg_means_b = [2.167]
    llm_means_b = [1.333]
    # CIs: KG [1.167, 2.833], LLM [0.333, 2.500]
    kg_err_b = [[2.167 - 1.167], [2.833 - 2.167]]
    llm_err_b = [[1.333 - 0.333], [2.500 - 1.333]]

    r1_b = ax2.bar(x_b - w/2, kg_means_b, w, yerr=kg_err_b, capsize=4, color=c_kg, edgecolor="#1A365D", linewidth=1.1)
    r2_b = ax2.bar(x_b + w/2, llm_means_b, w, yerr=llm_err_b, capsize=4, color=c_llm, edgecolor="#2D3748", linewidth=1.1)

    # Values cleanly placed above upper error bar caps
    ax2.text(r1_b[0].get_x() + r1_b[0].get_width()/2, 2.833 + 0.08, f"{kg_means_b[0]:.3f}",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=c_kg)
    ax2.text(r2_b[0].get_x() + r2_b[0].get_width()/2, 2.500 + 0.08, f"{llm_means_b[0]:.3f}",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#2D3748")

    ax2.text(0, 3.25, "p = 0.25 (n.s.)\n(Exploratory, dz=+0.85)", ha="center", va="bottom", fontsize=7.5, color="#2D3748")
    ax2.set_ylim(0, 3.7)
    ax2.set_xticks(x_b)
    ax2.set_xticklabels(metrics_b)
    ax2.set_title("(B) Out-of-Scope (n = 6)", loc="left", fontsize=10)

    # -------------------------------------------------------------
    # Panel C: Gold-Fact Coverage Rate (n=24 supported, 0-1.0 scale)
    # -------------------------------------------------------------
    ax3 = axes[2]
    metrics_c = ["Gold-Fact\nCoverage"]
    x_c = np.array([0])

    kg_means_c = [0.931]
    llm_means_c = [1.000]
    # CIs: KG [0.847, 1.000], LLM [1.000, 1.000]
    kg_err_c = [[0.931 - 0.847], [1.000 - 0.931]]
    llm_err_c = [[0.0], [0.0]]

    r1_c = ax3.bar(x_c - w/2, kg_means_c, w, yerr=kg_err_c, capsize=4, color=c_kg, edgecolor="#1A365D", linewidth=1.1)
    r2_c = ax3.bar(x_c + w/2, llm_means_c, w, yerr=llm_err_c, capsize=4, color=c_llm, edgecolor="#2D3748", linewidth=1.1)

    # Values cleanly placed above caps
    ax3.text(r1_c[0].get_x() + r1_c[0].get_width()/2, 1.05, f"{kg_means_c[0]:.3f}\n(56/60)",
             ha="center", va="bottom", fontsize=8, fontweight="bold", color=c_kg)
    ax3.text(r2_c[0].get_x() + r2_c[0].get_width()/2, 1.05, f"{llm_means_c[0]:.3f}\n(60/60)",
             ha="center", va="bottom", fontsize=8, fontweight="bold", color="#2D3748")

    ax3.text(0, 1.22, "p = 0.25 (n.s.)", ha="center", va="bottom", fontsize=7.5, color="#718096")
    ax3.set_ylabel("Coverage Rate (0.0–1.0)")
    ax3.set_ylim(0, 1.38)
    ax3.set_xticks(x_c)
    ax3.set_xticklabels(metrics_c)
    ax3.set_title("(C) Syllabus Coverage (n = 24)", loc="left", fontsize=10)

    plt.suptitle("Figure 3: Validated Double-Blind Human Evaluation Scores (95% Bootstrap CIs)",
                 fontsize=12, fontweight="bold", y=0.98)
    fig.text(0.98, 0.02, "Source: EduGraphAI Part 9K validated evaluation",
             ha="right", va="bottom", fontsize=8, fontstyle="italic", color="#718096")

    output_path = FIGURES_DIR / "Figure_3_Human_Evaluation_Scores.png"
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated Figure 3: {output_path}")


def generate_figure_4():
    """FIGURE 4: Local Benchmark Latency (Full N=120 Benchmark)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.4), dpi=300, gridspec_kw={"width_ratios": [1.1, 1.4]})

    # Load 120 latency observations from benchmark_results.json
    with open(BENCHMARK_RESULTS_PATH, "r", encoding="utf-8") as f:
        bench_data = json.load(f)["results"]

    kg_lat = np.array([item["kg_rag"]["latency_sec"] for item in bench_data])
    llm_lat = np.array([item["llm_only"]["latency_sec"] for item in bench_data])

    # -------------------------------------------------------------
    # Panel A: Mean Response Latency Comparison Bar Chart
    # -------------------------------------------------------------
    systems = ["LLM-Only\nBaseline", "EduGraphAI\nKG-RAG"]
    means = [20.190, 47.294]
    stds = [7.152, 15.654]
    colors = ["#718096", "#2B6CB0"]

    bars = ax1.bar(systems, means, yerr=[[0, 0], stds], capsize=5, width=0.48, color=colors, edgecolor="#1A202C", linewidth=1.1)

    # Place values above the standard deviation caps
    ax1.text(bars[0].get_x() + bars[0].get_width() / 2, means[0] + stds[0] + 1.5, f"{means[0]:.2f} s",
             ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#1A202C")
    ax1.text(bars[1].get_x() + bars[1].get_width() / 2, means[1] + stds[1] + 1.5, f"{means[1]:.2f} s",
             ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#1A202C")

    # Annotation Bracket for difference
    ax1.plot([0, 0, 1, 1], [68, 71, 71, 68], color="#C53030", lw=1.3)
    ax1.text(0.5, 72.5, "+27.104 s (+134%)\nLatency Multiplier: 2.34×",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#C53030")

    ax1.set_ylabel("Response Latency (seconds)")
    ax1.set_ylim(0, 84)
    ax1.set_title("(A) Mean Generation Latency (N = 120)", loc="left", fontsize=10)

    # -------------------------------------------------------------
    # Panel B: Distribution Boxplot with Jittered Observations
    # -------------------------------------------------------------
    bp = ax2.boxplot([llm_lat, kg_lat], tick_labels=["LLM-Only", "KG-RAG"], widths=0.4,
                     patch_artist=True, showmeans=True,
                     meanprops={"marker": "D", "markeredgecolor": "black", "markerfacecolor": "white", "markersize": 5})

    bp["boxes"][0].set_facecolor("#CBD5E0")
    bp["boxes"][1].set_facecolor("#90CDF4")
    for box in bp["boxes"]:
        box.set_alpha(0.8)

    # Jitter scatter plot overlay
    rng = np.random.default_rng(42)
    jitter_llm = rng.normal(1, 0.04, size=len(llm_lat))
    jitter_kg = rng.normal(2, 0.04, size=len(kg_lat))
    ax2.scatter(jitter_llm, llm_lat, color="#4A5568", alpha=0.35, s=14, zorder=3)
    ax2.scatter(jitter_kg, kg_lat, color="#2B6CB0", alpha=0.35, s=14, zorder=3)

    ax2.set_ylabel("Execution Time per Query (seconds)")
    ax2.set_xlim(0.4, 2.7)
    ax2.set_ylim(0, 125)
    ax2.set_title("(B) Full Benchmark Distribution (N = 120)", loc="left", fontsize=10)

    # Annotate Median and IQR inside margins
    ax2.text(0.52, 28.0, "Median: 17.18 s\nIQR: [14.6, 23.0]", fontsize=7.5, color="#4A5568",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#F7FAFC", edgecolor="#CBD5E0", alpha=0.9))
    ax2.text(2.18, 48.0, "Median: 38.96 s\nIQR: [35.2, 54.1]", fontsize=7.5, color="#2B6CB0",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#F0F8FF", edgecolor="#90CDF4", alpha=0.9))

    plt.suptitle("Figure 4: Local Benchmark Latency Comparison (Ollama llama3.2:latest, N = 120)",
                 fontsize=11.5, fontweight="bold", y=0.98)
    fig.text(0.08, 0.02, "*Note: Reflects local consumer runtime (Ollama 3B); does not represent cloud Groq llama-3.3-70b deployment.",
             ha="left", va="bottom", fontsize=8, fontstyle="italic", color="#4A5568")
    fig.text(0.98, 0.02, "Source: EduGraphAI Part 9K validated evaluation",
             ha="right", va="bottom", fontsize=8, fontstyle="italic", color="#718096")

    output_path = FIGURES_DIR / "Figure_4_Local_Benchmark_Latency.png"
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated Figure 4: {output_path}")


def main():
    set_academic_style()
    print("Generating Figure 1: EduGraphAI System Architecture...")
    generate_figure_1()
    print("Generating Figure 2: Evaluation Pipeline...")
    generate_figure_2()
    print("Generating Figure 3: Human Evaluation Scores...")
    generate_figure_3()
    print("Generating Figure 4: Local Benchmark Latency...")
    generate_figure_4()
    print("All four publication-ready figures successfully generated!")


if __name__ == "__main__":
    main()
