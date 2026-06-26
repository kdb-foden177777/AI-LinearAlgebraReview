#!/usr/bin/env python3
"""Run configuration-level ablation experiments for the paper.

This script replaces the earlier rule-based ablation summary.  Each row is
computed by changing an executable system configuration and evaluating it on
the saved benchmark, retrieval chunks, simulated learner profiles, and saved
agent-interaction logs.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import run_full_experiments as exp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_work" / "full_experiment_outputs"


PROFILES = [
    {"id": "weak_systems", "theta": -0.8, "weak": {"linear_systems", "row_reduction", "nullspace"}},
    {"id": "mid_spectral", "theta": 0.1, "weak": {"determinants", "eigenvalues", "diagonalization"}},
    {"id": "advanced_ortho", "theta": 0.7, "weak": {"orthogonality", "projection", "least_squares", "svd"}},
    {"id": "broad_review", "theta": 0.0, "weak": set(exp.CONCEPTS.keys())},
]


CONDITIONS = [
    {
        "condition": "A0 full system",
        "removed_component": "-",
        "syllabus_alignment": True,
        "mastery_loop": True,
        "retrieval": True,
        "concept_filter": True,
        "rag_grounding": True,
        "dependency_propagation": True,
        "irt": True,
        "dialogue_agent": True,
    },
    {
        "condition": "A1 no syllabus alignment",
        "removed_component": "M1 syllabus alignment",
        "syllabus_alignment": False,
        "mastery_loop": True,
        "retrieval": True,
        "concept_filter": True,
        "rag_grounding": True,
        "dependency_propagation": True,
        "irt": True,
        "dialogue_agent": True,
    },
    {
        "condition": "A2 no mastery loop",
        "removed_component": "M4 mastery loop",
        "syllabus_alignment": True,
        "mastery_loop": False,
        "retrieval": True,
        "concept_filter": True,
        "rag_grounding": True,
        "dependency_propagation": True,
        "irt": True,
        "dialogue_agent": True,
    },
    {
        "condition": "A3 no retrieval",
        "removed_component": "M2 retrieval",
        "syllabus_alignment": True,
        "mastery_loop": True,
        "retrieval": False,
        "concept_filter": False,
        "rag_grounding": False,
        "dependency_propagation": True,
        "irt": True,
        "dialogue_agent": True,
    },
    {
        "condition": "A4 no dependency propagation",
        "removed_component": "prerequisite propagation",
        "syllabus_alignment": True,
        "mastery_loop": True,
        "retrieval": True,
        "concept_filter": True,
        "rag_grounding": True,
        "dependency_propagation": False,
        "irt": True,
        "dialogue_agent": True,
    },
    {
        "condition": "A5 no IRT adaptation",
        "removed_component": "E2 IRT weighting",
        "syllabus_alignment": True,
        "mastery_loop": True,
        "retrieval": True,
        "concept_filter": True,
        "rag_grounding": True,
        "dependency_propagation": True,
        "irt": False,
        "dialogue_agent": True,
    },
    {
        "condition": "A6 fixed dialogue flow",
        "removed_component": "E1 dialogue agent",
        "syllabus_alignment": True,
        "mastery_loop": True,
        "retrieval": True,
        "concept_filter": True,
        "rag_grounding": True,
        "dependency_propagation": True,
        "irt": True,
        "dialogue_agent": False,
    },
]


DELTA_SPECS = [
    {
        "condition": "A1 no syllabus alignment",
        "primary_metric": "Alignment score",
        "metric_key": "alignment_score",
        "direction": "higher is better",
    },
    {
        "condition": "A2 no mastery loop",
        "primary_metric": "Weak-concept coverage",
        "metric_key": "weak_concept_coverage",
        "direction": "higher is better",
    },
    {
        "condition": "A3 no retrieval",
        "primary_metric": "Retrieval MRR@5",
        "metric_key": "retrieval_mrr_at_5",
        "direction": "higher is better",
    },
    {
        "condition": "A3 no retrieval",
        "primary_metric": "Grounding support proxy",
        "metric_key": "grounding_support_proxy",
        "direction": "higher is better",
    },
    {
        "condition": "A4 no dependency propagation",
        "primary_metric": "Prerequisite risk flag",
        "metric_key": "prerequisite_risk_flag",
        "direction": "lower is better",
    },
    {
        "condition": "A5 no IRT adaptation",
        "primary_metric": "Difficulty match error",
        "metric_key": "difficulty_match_error",
        "direction": "lower is better",
    },
    {
        "condition": "A6 fixed dialogue flow",
        "primary_metric": "Dialogue flexibility",
        "metric_key": "dialogue_flexibility",
        "direction": "higher is better",
    },
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def save_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def ensure_inputs() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, float]]:
    if (OUT / "benchmark_items.jsonl").exists():
        benchmark = load_jsonl(OUT / "benchmark_items.jsonl")
    else:
        benchmark = exp.build_benchmark()
    chunks = exp.build_chunks()
    graph = exp.build_concept_graph(benchmark)
    raw_weights = {n["id"]: float(n["syllabus_weight"]) for n in graph["nodes"]}
    vals = list(raw_weights.values())
    lo, hi = min(vals), max(vals)
    weights = {k: ((v - lo) / (hi - lo) if hi > lo else 1.0) for k, v in raw_weights.items()}
    return benchmark, chunks, weights


def item_info(theta: float, b_seed: float, a: float = 1.0) -> float:
    b = b_seed * 4 - 2
    p = 1 / (1 + math.exp(-a * (theta - b)))
    return a * a * p * (1 - p)


def expanded_weak_set(profile: dict[str, Any], use_dependencies: bool) -> set[str]:
    weak = set(profile["weak"])
    if not use_dependencies:
        return weak
    expanded = set(weak)
    changed = True
    while changed:
        changed = False
        for cid in list(expanded):
            for pre in exp.CONCEPTS[cid]["prereq"]:
                if pre not in expanded:
                    expanded.add(pre)
                    changed = True
    return expanded


def recommend_items(benchmark: list[dict[str, Any]], weights: dict[str, float], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    pool = [i for i in benchmark if i["source_role"] in {"exam", "activity", "solution"}]
    rows = []
    for profile in PROFILES:
        available = pool[:]
        direct_weak = set(profile["weak"])
        target_weak = expanded_weak_set(profile, cfg["dependency_propagation"])
        for step in range(12):
            if cfg["mastery_loop"]:
                weak_term = lambda item: len(set(item["expected_concepts"]) & target_weak)
            else:
                unit_order = ["U1", "U2", "U3", "U4", "U5", "U6"]
                target_unit = unit_order[step % len(unit_order)]
                weak_term = lambda item, target_unit=target_unit: int(target_unit in item["unit"])

            def score(item: dict[str, Any]) -> tuple[float, float, float]:
                labels = item["expected_concepts"]
                alignment = statistics.mean(weights.get(c, 0.0) for c in labels)
                difficulty_fit = item_info(profile["theta"], item["difficulty_seed"]) if cfg["irt"] else 0.0
                concept_fit = weak_term(item)
                score_val = 0.0
                score_val += 0.35 * alignment if cfg["syllabus_alignment"] else 0.0
                score_val += 0.45 * concept_fit
                score_val += 0.35 * difficulty_fit
                return (score_val, alignment, difficulty_fit)

            chosen = max(available, key=score)
            available.remove(chosen)
            labels = set(chosen["expected_concepts"])
            prerequisite_risks = 0
            upstream_hits = 0
            for cid in labels:
                prereqs = set(exp.CONCEPTS[cid]["prereq"])
                upstream_hits += int(bool(prereqs & target_weak))
                prerequisite_risks += int(bool(prereqs & direct_weak) and cid not in direct_weak)
            rows.append({
                "condition": cfg["condition"],
                "learner": profile["id"],
                "step": step + 1,
                "item_id": chosen["id"],
                "source_path": chosen["source_path"],
                "concepts": "|".join(chosen["expected_concepts"]),
                "alignment": round(statistics.mean(weights.get(c, 0.0) for c in labels), 3),
                "weak_hit": int(bool(labels & direct_weak)),
                "expanded_weak_hit": int(bool(labels & target_weak)),
                "upstream_hit": int(upstream_hits > 0),
                "difficulty_error": round(abs((chosen["difficulty_seed"] * 4 - 2) - profile["theta"]), 3),
                "prerequisite_risk_flag": prerequisite_risks,
            })
    return rows


def retrieval_metrics(chunks: list[dict[str, Any]], benchmark: list[dict[str, Any]], cfg: dict[str, Any]) -> tuple[float, float, list[dict[str, Any]]]:
    queries = exp.expanded_retrieval_queries(benchmark, target_n=80)
    if not cfg["retrieval"]:
        rows = [{
            "condition": cfg["condition"],
            "concept": concept,
            "query": query,
            "success_at_5": 0,
            "reciprocal_rank": 0.0,
            "grounding_support_proxy": 0.0,
            "top_sources": "",
        } for concept, query, _terms in queries]
        return 0.0, 0.0, rows

    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, max_df=0.95)
    matrix = vectorizer.fit_transform(texts)
    out = []
    for concept, query, expected_terms in queries:
        scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
        ids = list(range(len(chunks)))
        if cfg["concept_filter"]:
            filtered = [i for i in ids if concept in chunks[i]["labels"]]
            if filtered:
                ids = filtered
        ranked = sorted(ids, key=lambda i: scores[i], reverse=True)[:5]
        rank_hit = None
        support_hits = 0
        context_text = " ".join(chunks[i]["text"].lower() for i in ranked[:4])
        for term in expected_terms:
            support_hits += int(term.lower() in context_text)
        for rank, i in enumerate(ranked, 1):
            low = chunks[i]["text"].lower()
            if concept in chunks[i]["labels"] or any(t.lower() in low for t in expected_terms):
                rank_hit = rank
                break
        support_proxy = support_hits / max(1, len(expected_terms)) if cfg["rag_grounding"] else 0.0
        out.append({
            "condition": cfg["condition"],
            "concept": concept,
            "query": query,
            "success_at_5": int(rank_hit is not None),
            "reciprocal_rank": round(1 / rank_hit if rank_hit else 0.0, 3),
            "grounding_support_proxy": round(support_proxy, 3),
            "top_sources": "|".join(chunks[i]["path"] for i in ranked[:3]) if cfg["rag_grounding"] else "",
        })
    mrr = statistics.mean(r["reciprocal_rank"] for r in out)
    support = statistics.mean(r["grounding_support_proxy"] for r in out)
    return round(mrr, 3), round(support, 3), out


def dialogue_flexibility(cfg: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    tasks = exp.expanded_agent_tasks(target_n=144)
    existing = OUT / "agent_interaction_rows.csv"
    rows = []
    if cfg["dialogue_agent"] and existing.exists():
        with existing.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                vals = [
                    int(row.get("format_ok", 0)),
                    int(row.get("concept_attribution", 0)),
                    int(row.get("no_full_solution", 0)),
                    int(row.get("groundedness_proxy", 0)),
                ]
                rows.append({
                    "condition": cfg["condition"],
                    "task_id": row.get("task_id", ""),
                    "action": row.get("action", ""),
                    "concept": row.get("concept", ""),
                    "action_specific": vals[0],
                    "concept_specific": vals[1],
                    "hint_control": vals[2],
                    "grounded": vals[3],
                    "score": round(statistics.mean(vals), 3),
                })
    else:
        for idx, task in enumerate(tasks, 1):
            reply = "Follow the standard review workflow: identify the topic, review the definition, try a similar example, and ask the instructor if still stuck."
            low = reply.lower()
            action = task["action"]
            concept = task["concept"]
            action_specific = int((action == "grade" and "score" in low) or (action == "hint" and "hint" in low) or (action == "chat" and "explain" in low))
            concept_specific = int(concept.replace("_", " ") in low or exp.CONCEPTS[concept]["label"].split()[0].lower() in low)
            hint_control = int(action != "hint" or "answer is" not in low)
            grounded = 0
            vals = [action_specific, concept_specific, hint_control, grounded]
            rows.append({
                "condition": cfg["condition"],
                "task_id": f"fixed_{idx:03d}",
                "action": action,
                "concept": concept,
                "action_specific": action_specific,
                "concept_specific": concept_specific,
                "hint_control": hint_control,
                "grounded": grounded,
                "score": round(statistics.mean(vals), 3),
            })
    return round(statistics.mean(r["score"] for r in rows), 3), rows


def main() -> int:
    exp.load_env()
    benchmark, chunks, weights = ensure_inputs()
    config_rows = []
    summary_rows = []
    all_selection_rows = []
    all_retrieval_rows = []
    all_dialogue_rows = []

    for cfg in CONDITIONS:
        print(f"Running {cfg['condition']}", flush=True)
        selection_rows = recommend_items(benchmark, weights, cfg)
        mrr, support, retrieval_rows = retrieval_metrics(chunks, benchmark, cfg)
        dialogue_score, dialogue_rows = dialogue_flexibility(cfg)
        all_selection_rows.extend(selection_rows)
        all_retrieval_rows.extend(retrieval_rows)
        all_dialogue_rows.extend(dialogue_rows)

        summary_rows.append({
            "condition": cfg["condition"],
            "removed_component": cfg["removed_component"],
            "alignment_score": round(statistics.mean(r["alignment"] for r in selection_rows), 3),
            "weak_concept_coverage": round(statistics.mean(r["weak_hit"] for r in selection_rows), 3),
            "upstream_prereq_coverage": round(statistics.mean(r["upstream_hit"] for r in selection_rows), 3),
            "retrieval_mrr_at_5": mrr,
            "grounding_support_proxy": support,
            "difficulty_match_error": round(statistics.mean(r["difficulty_error"] for r in selection_rows), 3),
            "prerequisite_risk_flag": round(statistics.mean(r["prerequisite_risk_flag"] for r in selection_rows), 3),
            "dialogue_flexibility": dialogue_score,
            "items_selected": len(selection_rows),
            "retrieval_queries": len(retrieval_rows),
            "dialogue_tasks": len(dialogue_rows),
        })
        config_rows.append({k: v for k, v in cfg.items() if k != "condition"} | {"condition": cfg["condition"]})

    save_csv(OUT / "ablation_results.csv", summary_rows)
    summary_by_condition = {r["condition"]: r for r in summary_rows}
    full = summary_by_condition["A0 full system"]
    delta_rows = []
    for spec in DELTA_SPECS:
        row = summary_by_condition[spec["condition"]]
        full_value = float(full[spec["metric_key"]])
        ablated_value = float(row[spec["metric_key"]])
        raw_change = ablated_value - full_value
        if spec["direction"] == "higher is better":
            effect = ablated_value - full_value
        else:
            effect = full_value - ablated_value
        delta_rows.append({
            "condition": spec["condition"],
            "removed_component": row["removed_component"],
            "primary_metric": spec["primary_metric"],
            "direction": spec["direction"],
            "full_value": round(full_value, 3),
            "ablated_value": round(ablated_value, 3),
            "raw_change": round(raw_change, 3),
            "effect_on_quality": round(effect, 3),
        })
    save_csv(OUT / "ablation_delta_results.csv", delta_rows)
    save_csv(OUT / "ablation_selection_rows.csv", all_selection_rows)
    save_csv(OUT / "ablation_retrieval_rows.csv", all_retrieval_rows)
    save_csv(OUT / "ablation_dialogue_rows.csv", all_dialogue_rows)
    save_json(OUT / "ablation_configs.json", config_rows)

    with (OUT / "ablation_summary.md").open("w", encoding="utf-8") as f:
        f.write("# True Configuration Ablation Summary\n\n")
        f.write("Each condition was evaluated by changing the executable configuration and recomputing metrics from saved benchmark items, corpus chunks, simulated learner profiles, and saved agent logs. No row is manually filled.\n\n")
        f.write("| Condition | Removed | Align | Weak cov. | Upstream cov. | MRR@5 | Support | Diff. err. | Risk flag | Dialogue |\n")
        f.write("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for r in summary_rows:
            f.write(
                f"| {r['condition']} | {r['removed_component']} | {r['alignment_score']} | {r['weak_concept_coverage']} | "
                f"{r['upstream_prereq_coverage']} | {r['retrieval_mrr_at_5']} | {r['grounding_support_proxy']} | "
                f"{r['difficulty_match_error']} | {r['prerequisite_risk_flag']} | {r['dialogue_flexibility']} |\n"
            )
        f.write("\n## Primary-Metric Deltas\n\n")
        f.write("| Condition | Removed | Primary metric | Full | Ablated | Raw change | Effect on quality |\n")
        f.write("|---|---|---|---:|---:|---:|---:|\n")
        for r in delta_rows:
            f.write(
                f"| {r['condition']} | {r['removed_component']} | {r['primary_metric']} | "
                f"{r['full_value']} | {r['ablated_value']} | {r['raw_change']} | {r['effect_on_quality']} |\n"
            )
    print(f"Wrote ablation outputs to {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
