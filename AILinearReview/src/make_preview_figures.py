#!/usr/bin/env python3
"""Generate preview figures from the current experiment outputs.

The figures are candidates for the manuscript. They are intentionally saved
outside the LaTeX manuscript folder until selected by the user.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_work" / "full_experiment_outputs"
FIG = ROOT / "paper_work" / "figures_preview"
FIG.mkdir(parents=True, exist_ok=True)


COLORS = {
    "blue": "#4C78A8",
    "teal": "#54A24B",
    "orange": "#F58518",
    "red": "#E45756",
    "purple": "#B279A2",
    "gray": "#6B7280",
    "light_gray": "#E5E7EB",
}


def load_json(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def savefig(name: str) -> None:
    for ext in ["png", "pdf", "svg"]:
        path = FIG / f"{name}.{ext}"
        plt.savefig(path, bbox_inches="tight", dpi=320)
    plt.close()


def style_axes(ax, ylim=(0, 1.08), ylabel="Score") -> None:
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color=COLORS["light_gray"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def add_labels(ax, bars, fmt="{:.3f}", dy=0.02, fontsize=8) -> None:
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + dy,
            fmt.format(h),
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color="#333333",
        )


def retrieval_performance() -> None:
    data = load_json("retrieval_metrics.json")
    order = ["lexical", "lecture_only", "exam_only", "concept_filtered"]
    labels = ["Lexical", "Lecture only", "Exam only", "Concept filtered"]
    success = [data[k]["success_at_5"] for k in order]
    mrr = [data[k]["mrr_at_5"] for k in order]

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    x = np.arange(len(order))
    w = 0.34
    b1 = ax.bar(x - w / 2, success, width=w, color=COLORS["blue"], label="Success@5")
    b2 = ax.bar(x + w / 2, mrr, width=w, color=COLORS["orange"], label="MRR@5")
    style_axes(ax)
    add_labels(ax, b1)
    add_labels(ax, b2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Retrieval benchmark by retrieval condition", pad=12)
    ax.legend(frameon=False, ncols=2, loc="upper left")
    ax.text(0.99, -0.25, "80 queries per condition", transform=ax.transAxes, ha="right", fontsize=8, color=COLORS["gray"])
    savefig("fig1_retrieval_performance")


def agent_metrics() -> None:
    data = load_json("agent_metrics.json")
    metrics = [
        ("Format compliance", data["format_compliance_rate"], COLORS["teal"]),
        ("No full solution", data["hint_no_full_solution_rate"], COLORS["blue"]),
        ("Completed response", data["completed_response_rate"], COLORS["purple"]),
        ("Concept attribution", data["concept_attribution_rate"], COLORS["orange"]),
        ("Groundedness proxy", data["groundedness_proxy_rate"], COLORS["red"]),
    ]
    labels, values, colors = zip(*metrics)

    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=colors, height=0.58)
    ax.set_xlim(0, 1.08)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Rate")
    ax.grid(axis="x", color=COLORS["light_gray"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(value + 0.018, bar.get_y() + bar.get_height() / 2, f"{value:.3f}", va="center", fontsize=8)
    ax.set_title("Agent interaction benchmark metrics", pad=12)
    ax.text(
        0.99,
        -0.18,
        f"144 tasks: 48 grading, 48 hint, 48 dialogue; API errors={data['api_error_count']}",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color=COLORS["gray"],
    )
    savefig("fig2_agent_metrics")


def ablation_overview() -> None:
    rows = []
    with (OUT / "ablation_results.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    conditions = [r["condition"] for r in rows]
    short = ["Full", "No graph", "No filter", "No RAG", "No IRT"]
    metrics = [
        ("Retrieval MRR", "retrieval_mrr", COLORS["blue"]),
        ("RAG support", "rag_support", COLORS["teal"]),
        ("Agent quality", "agent_quality", COLORS["orange"]),
        ("Adaptive score", "adaptive_score", COLORS["purple"]),
    ]

    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    x = np.arange(len(conditions))
    w = 0.18
    for i, (label, key, color) in enumerate(metrics):
        vals = [float(r[key]) for r in rows]
        ax.bar(x + (i - 1.5) * w, vals, width=w, label=label, color=color)
    style_axes(ax)
    ax.set_xticks(x)
    ax.set_xticklabels(short)
    ax.set_title("Ablation analysis across system components", pad=12)
    ax.legend(frameon=False, ncols=4, loc="upper center", bbox_to_anchor=(0.5, 1.02), fontsize=8)
    ax.text(0.99, -0.25, "Higher is better for all displayed metrics", transform=ax.transAxes, ha="right", fontsize=8, color=COLORS["gray"])
    savefig("fig3_ablation_overview")


def irt_policy_comparison() -> None:
    data = load_json("irt_simulation_metrics.json")
    order = ["random", "difficulty_only", "graph_only", "graph_irt"]
    labels = ["Random", "Difficulty only", "Graph only", "Graph+IRT"]

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.4), gridspec_kw={"width_ratios": [1.25, 1]})
    x = np.arange(len(order))
    w = 0.36
    coverage = [data[k]["weak_concept_coverage"] for k in order]
    violation = [data[k]["prerequisite_violation_rate"] for k in order]
    b1 = axes[0].bar(x - w / 2, coverage, width=w, color=COLORS["teal"], label="Weak-concept coverage")
    b2 = axes[0].bar(x + w / 2, violation, width=w, color=COLORS["red"], label="Prerequisite violation")
    style_axes(axes[0], ylabel="Rate")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=15, ha="right")
    axes[0].legend(frameon=False, fontsize=8)

    diff = [data[k]["difficulty_match_error"] for k in order]
    div = [data[k]["concept_diversity"] for k in order]
    axes[1].plot(labels, diff, marker="o", linewidth=2, color=COLORS["blue"], label="Difficulty error")
    axes[1].set_ylabel("Difficulty match error")
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].grid(axis="y", color=COLORS["light_gray"])
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    ax2 = axes[1].twinx()
    ax2.plot(labels, div, marker="s", linewidth=2, color=COLORS["purple"], label="Concept diversity")
    ax2.set_ylabel("Concept diversity")
    ax2.spines["top"].set_visible(False)
    lines, labs = axes[1].get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    axes[1].legend(lines + lines2, labs + labs2, frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("IRT policy simulation trade-offs", y=1.04)
    savefig("fig4_irt_policy_comparison")


def corpus_composition() -> None:
    summary = load_json("full_pipeline_summary.json")
    folders = summary["audit"]["folders"]
    labels = ["Slides", "Flipped", "MIT finals"]
    files = [r["files"] for r in folders]
    tokens = [r["approx_tokens"] / 1000 for r in folders]

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    x = np.arange(len(labels))
    bars = ax.bar(x, tokens, color=[COLORS["blue"], COLORS["teal"], COLORS["orange"]], width=0.55)
    ax.set_ylabel("Approx. tokens (thousands)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid(axis="y", color=COLORS["light_gray"])
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, f in zip(bars, files):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 8, f"{h:.0f}k\n{f} files", ha="center", va="bottom", fontsize=8)
    ax.set_title("Converted Markdown corpus composition", pad=12)
    ax.text(0.99, -0.20, "Total: 200 files, about 545k tokens", transform=ax.transAxes, ha="right", fontsize=8, color=COLORS["gray"])
    savefig("fig5_corpus_composition")


def make_contact_sheet() -> None:
    from PIL import Image, ImageDraw

    files = sorted(FIG.glob("fig*.png"))
    thumbs = []
    for p in files:
        img = Image.open(p).convert("RGB")
        img.thumbnail((720, 360))
        canvas = Image.new("RGB", (760, 410), "white")
        canvas.paste(img, ((760 - img.width) // 2, 10))
        draw = ImageDraw.Draw(canvas)
        draw.text((20, 380), p.name, fill=(60, 60, 60))
        thumbs.append(canvas)
    w, h = 1520, 1230
    sheet = Image.new("RGB", (w, h), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 2) * 760, (i // 2) * 410))
    sheet.save(FIG / "candidate_figures_contact_sheet.png", quality=95)


def main() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })
    retrieval_performance()
    agent_metrics()
    ablation_overview()
    irt_policy_comparison()
    corpus_composition()
    make_contact_sheet()
    print(f"Wrote preview figures to {FIG}")


if __name__ == "__main__":
    main()
