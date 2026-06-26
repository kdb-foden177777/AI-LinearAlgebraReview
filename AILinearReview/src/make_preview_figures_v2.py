#!/usr/bin/env python3
"""Generate refined manuscript-style preview figures.

This version uses a restrained blue-gray palette, fewer chart elements, and
more information-dense designs than the first preview batch.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_work" / "full_experiment_outputs"
FIG = ROOT / "paper_work" / "figures_preview_v2"
FIG.mkdir(parents=True, exist_ok=True)


INK = "#1F2937"
MUTED = "#6B7280"
GRID = "#E5E7EB"
PALE = "#D7DEE8"
MID = "#7C8DA6"
BLUE = "#2F5D8C"
DEEP = "#17324D"
WARM = "#8A6F4D"


def load_json(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def load_retrieval_metrics():
    expanded = OUT / "retrieval_metrics_expanded.json"
    if expanded.exists():
        payload = json.loads(expanded.read_text(encoding="utf-8"))
        return {row["condition"]: row for row in payload["conditions"]}, payload["query_count"]
    data = load_json("retrieval_metrics.json")
    return data, data["lexical"]["queries"]


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 10,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.edgecolor": INK,
            "axes.linewidth": 0.8,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def clean_axes(ax, grid_axis="x") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=INK, length=3, width=0.7)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)


def save(name: str) -> None:
    for ext in ["png", "pdf", "svg"]:
        plt.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=360)
    plt.close()


def fig_retrieval_slope() -> None:
    data, query_count = load_retrieval_metrics()
    order = ["lecture_only", "exam_only", "lexical", "concept_filtered"]
    labels = ["Lecture only", "Exam only", "Lexical", "Concept filtered"]
    success = np.array([data[k]["success_at_5"] for k in order])
    mrr = np.array([data[k]["mrr_at_5"] for k in order])
    y = np.arange(len(order))

    fig, ax = plt.subplots(figsize=(6.4, 3.45))
    for i in y:
        color = DEEP if order[i] == "concept_filtered" else "#AAB5C4"
        ax.plot([mrr[i], success[i]], [i, i], color=color, linewidth=2.2, solid_capstyle="round")
    ax.scatter(mrr, y, s=44, color=PALE, edgecolor=INK, linewidth=0.6, label="MRR@5", zorder=3)
    ax.scatter(success, y, s=54, color=[DEEP if k == "concept_filtered" else MID for k in order], edgecolor=INK, linewidth=0.6, label="Success@5", zorder=3)
    for i, (s, m) in enumerate(zip(success, mrr)):
        if abs(s - m) < 0.006:
            ax.text(s + 0.018, i, f"{s:.3f}", va="center", ha="left", fontsize=8, color=INK)
        else:
            ax.text(s + 0.018, i, f"{s:.3f}", va="center", ha="left", fontsize=8, color=INK)
            ax.text(m - 0.018, i, f"{m:.3f}", va="center", ha="right", fontsize=8, color=MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0.40, 1.06)
    ax.set_xlabel("Score")
    ax.set_title("Retrieval improves when ranking is constrained by concept labels", loc="left", pad=10)
    clean_axes(ax, "x")
    ax.legend(frameon=False, loc="lower right", ncols=2)
    ax.text(0.0, -0.18, f"Each row connects MRR@5 to Success@5; {query_count} queries per condition.", transform=ax.transAxes, color=MUTED, fontsize=8)
    save("v2_fig1_retrieval_slope")


def fig_agent_lollipop() -> None:
    data = load_json("agent_metrics.json")
    items = [
        ("Format\ncompliance", data["format_compliance_rate"]),
        ("No full\nsolution", data["hint_no_full_solution_rate"]),
        ("Completed\nresponse", data["completed_response_rate"]),
        ("Concept\nattribution", data["concept_attribution_rate"]),
        ("Grounding\nproxy", data["groundedness_proxy_rate"]),
    ]
    labels, vals = zip(*items)
    x = np.arange(len(vals))

    fig, ax = plt.subplots(figsize=(6.5, 3.25))
    ax.vlines(x, 0, vals, color="#B8C2D0", linewidth=5, alpha=0.85)
    colors = [DEEP, DEEP, BLUE, MID, MID]
    ax.scatter(x, vals, s=160, color=colors, edgecolor="white", linewidth=1.4, zorder=3)
    for xi, v in zip(x, vals):
        ax.text(xi, v + 0.035, f"{v:.3f}", ha="center", va="bottom", color=INK, fontsize=8)
    ax.axhline(0.8, color="#CBD5E1", linewidth=0.9, linestyle=(0, (3, 3)))
    ax.text(len(vals) - 0.25, 0.805, "0.80", color=MUTED, fontsize=7, va="bottom")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Rate")
    ax.set_title("Agent reliability and grounding across 144 interaction tasks", loc="left", pad=10)
    clean_axes(ax, "y")
    ax.text(0.0, -0.24, f"Balanced benchmark: 48 grading, 48 hint, 48 dialogue; API errors={data['api_error_count']}.", transform=ax.transAxes, color=MUTED, fontsize=8)
    save("v2_fig2_agent_lollipop")


def fig_ablation_heatmap() -> None:
    with (OUT / "ablation_delta_results.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    labels = [
        f"{r['condition'].replace(' no ', ' no ').replace(' fixed ', ' fixed ')}\n{r['primary_metric']}"
        for r in rows
    ]
    effects = np.array([float(r["effect_on_quality"]) for r in rows])
    loss = -effects
    y = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(7.3, 3.9))
    colors = [DEEP if v >= 0.25 else MID if v >= 0.04 else "#B8C2D0" for v in loss]
    ax.barh(y, loss, color=colors, height=0.58)
    for yi, value in zip(y, loss):
        offset = 0.026 if value >= 0.035 else 0.035
        ax.text(value + offset, yi, f"{value:.3f}", va="center", ha="left", color=INK, fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(loss) * 1.18)
    ax.set_xlabel("Target-metric degradation after removing the component")
    ax.set_title("Primary ablation effects from executable component removals", loc="left", pad=10)
    clean_axes(ax, "x")
    ax.text(0.0, -0.22, "Each row reports only the metric targeted by that ablation; larger values indicate larger quality loss.", transform=ax.transAxes, color=MUTED, fontsize=8)
    save("v2_fig3_ablation_heatmap")


def fig_irt_quadrant() -> None:
    data = load_json("irt_simulation_metrics.json")
    order = ["random", "difficulty_only", "graph_only", "graph_irt"]
    labels = ["Random", "Difficulty only", "Graph only", "Graph+IRT"]
    col_labels = [
        "Weak-concept\ncoverage ↑",
        "Difficulty\nerror ↓",
        "Concept\ndiversity ↑",
        "Prerequisite\nrisk flag ↓",
    ]
    raw = np.array(
        [
            [
                data[k]["weak_concept_coverage"],
                data[k]["difficulty_match_error"],
                data[k]["concept_diversity"],
                data[k]["prerequisite_violation_rate"],
            ]
            for k in order
        ]
    )

    desirability = np.zeros_like(raw, dtype=float)
    desirability[:, 0] = raw[:, 0]
    desirability[:, 2] = raw[:, 2] / raw[:, 2].max()
    for j in [1, 3]:
        lo, hi = raw[:, j].min(), raw[:, j].max()
        desirability[:, j] = 1 - (raw[:, j] - lo) / (hi - lo)

    cmap = LinearSegmentedColormap.from_list("policy_profile", ["#F8FAFC", "#CBD6E5", "#7890AC", "#17324D"])
    fig, ax = plt.subplots(figsize=(6.7, 3.35))
    im = ax.imshow(desirability, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    for i in range(raw.shape[0]):
        for j in range(raw.shape[1]):
            val = raw[i, j]
            color = "white" if desirability[i, j] > 0.64 else INK
            text = f"{val:.3f}" if j != 2 else f"{val:.2f}"
            ax.text(j, i, text, ha="center", va="center", color=color, fontsize=8)
    ax.set_title("Adaptive-selection policy profiles across four metrics", loc="left", pad=10)
    ax.set_xlabel("Darker cells indicate stronger direction-aware performance")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    ax.set_xticks(np.arange(-0.5, len(col_labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.025)
    cbar.set_label("Relative desirability", fontsize=8)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(labelsize=7, length=2)
    ax.text(0.0, -0.27, "Cell labels are raw simulation values; prerequisite risk is an automatic proxy flag.", transform=ax.transAxes, color=MUTED, fontsize=8)
    save("v2_fig4_irt_quadrant")


def fig_corpus_token_balance() -> None:
    summary = load_json("full_pipeline_summary.json")
    folders = summary["audit"]["folders"]
    labels = ["Slides", "Flipped", "MIT finals"]
    tokens = np.array([r["approx_tokens"] for r in folders], dtype=float)
    files = [r["files"] for r in folders]
    share = tokens / tokens.sum()

    fig, ax = plt.subplots(figsize=(6.2, 2.2))
    left = 0
    colors = [DEEP, "#8AA0B8", "#B7C3D1"]
    for lab, sh, tok, f, col in zip(labels, share, tokens, files, colors):
        ax.barh([0], [sh], left=left, color=col, height=0.38)
        if sh < 0.13:
            ax.text(left + sh / 2, 0.33, f"{lab}\n{tok/1000:.0f}k / {f} files", ha="center", va="bottom", fontsize=8, color=INK)
            ax.plot([left + sh / 2, left + sh / 2], [0.21, 0.02], color=MUTED, linewidth=0.6)
        else:
            ax.text(left + sh / 2, 0, f"{lab}\n{tok/1000:.0f}k tokens\n{f} files", ha="center", va="center", fontsize=8, color="white" if sh > 0.22 else INK)
        left += sh
    ax.set_ylim(-0.32, 0.52)
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "25", "50", "75", "100%"])
    ax.set_xlabel("Share of converted corpus by approximate token count")
    ax.set_title("Corpus balance across converted Markdown sources", loc="left", pad=8)
    clean_axes(ax, "x")
    ax.spines["left"].set_visible(False)
    save("v2_fig5_corpus_balance")


def contact_sheet() -> None:
    from PIL import Image, ImageDraw

    files = sorted(FIG.glob("v2_fig*.png"))
    cards = []
    for p in files:
        img = Image.open(p).convert("RGB")
        img.thumbnail((760, 390))
        card = Image.new("RGB", (800, 450), "white")
        card.paste(img, ((800 - img.width) // 2, 8))
        draw = ImageDraw.Draw(card)
        draw.text((18, 420), p.name, fill=(70, 70, 70))
        cards.append(card)
    sheet = Image.new("RGB", (1600, 1350), "white")
    for i, card in enumerate(cards):
        sheet.paste(card, ((i % 2) * 800, (i // 2) * 450))
    sheet.save(FIG / "candidate_figures_v2_contact_sheet.png", quality=95)


def main() -> None:
    setup()
    fig_retrieval_slope()
    fig_agent_lollipop()
    fig_ablation_heatmap()
    fig_irt_quadrant()
    fig_corpus_token_balance()
    contact_sheet()
    print(f"Wrote refined preview figures to {FIG}")


if __name__ == "__main__":
    main()
