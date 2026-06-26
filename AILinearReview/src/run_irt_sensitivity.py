#!/usr/bin/env python3
"""Run an IRT sensitivity experiment under fixed concept targets.

The original adaptive-selection simulation mixes concept coverage and difficulty
matching. This script isolates the IRT question: once a weak target concept is
fixed, does IRT-style item information select difficulty-appropriate items more
reliably than non-IRT policies?
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

import run_full_experiments as exp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_work" / "full_experiment_outputs"
OUT.mkdir(parents=True, exist_ok=True)

RNG = random.Random(1806)

PROFILES = [
    {"id": "weak_systems", "theta": -0.8, "weak": {"linear_systems", "row_reduction", "nullspace"}},
    {"id": "mid_spectral", "theta": 0.1, "weak": {"determinants", "eigenvalues", "diagonalization"}},
    {"id": "advanced_ortho", "theta": 0.7, "weak": {"orthogonality", "projection", "least_squares", "svd"}},
    {"id": "broad_review", "theta": 0.0, "weak": set(exp.CONCEPTS.keys())},
]

POLICIES = [
    "random_within_target",
    "syllabus_ranked",
    "difficulty_only",
    "graph_irt",
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


def load_benchmark() -> list[dict[str, Any]]:
    path = OUT / "benchmark_items.jsonl"
    if path.exists():
        return load_jsonl(path)
    return exp.build_benchmark()


def concept_weights(benchmark: list[dict[str, Any]]) -> dict[str, float]:
    graph = exp.build_concept_graph(benchmark)
    raw = {n["id"]: float(n["syllabus_weight"]) for n in graph["nodes"]}
    lo, hi = min(raw.values()), max(raw.values())
    return {k: ((v - lo) / (hi - lo) if hi > lo else 1.0) for k, v in raw.items()}


def difficulty_value(item: dict[str, Any]) -> float:
    return item["difficulty_seed"] * 4 - 2


def item_information(theta: float, item: dict[str, Any], a: float = 1.0) -> float:
    b = difficulty_value(item)
    p = 1 / (1 + math.exp(-a * (theta - b)))
    return a * a * p * (1 - p)


def choose_item(policy: str, pool: list[dict[str, Any]], theta: float, target: str, weights: dict[str, float]) -> dict[str, Any]:
    if policy == "random_within_target":
        return RNG.choice(pool)
    if policy == "syllabus_ranked":
        return max(
            pool,
            key=lambda item: (
                statistics.mean(weights.get(c, 0.0) for c in item["expected_concepts"]),
                len(item["expected_concepts"]),
            ),
        )
    if policy == "difficulty_only":
        return min(pool, key=lambda item: abs(difficulty_value(item) - theta))
    if policy == "graph_irt":
        return max(
            pool,
            key=lambda item: (
                item_information(theta, item)
                + 0.08 * statistics.mean(weights.get(c, 0.0) for c in item["expected_concepts"])
                + 0.04 * int(target in item["expected_concepts"])
            ),
        )
    raise ValueError(f"Unknown policy: {policy}")


def run() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    benchmark = load_benchmark()
    weights = concept_weights(benchmark)
    items = [i for i in benchmark if i["source_role"] in {"exam", "activity", "solution"}]
    rows: list[dict[str, Any]] = []

    for profile in PROFILES:
        for target in sorted(profile["weak"]):
            pool = [i for i in items if target in set(i["expected_concepts"])]
            if len(pool) < 2:
                continue
            for policy in POLICIES:
                chosen = choose_item(policy, pool, profile["theta"], target, weights)
                diff_error = abs(difficulty_value(chosen) - profile["theta"])
                rows.append({
                    "learner": profile["id"],
                    "theta": profile["theta"],
                    "target_concept": target,
                    "policy": policy,
                    "candidate_count": len(pool),
                    "item_id": chosen["id"],
                    "source_role": chosen["source_role"],
                    "source_path": chosen["source_path"],
                    "item_difficulty": round(difficulty_value(chosen), 3),
                    "difficulty_error": round(diff_error, 3),
                    "difficulty_hit_0_5": int(diff_error <= 0.5),
                    "difficulty_hit_0_75": int(diff_error <= 0.75),
                    "item_information": round(item_information(profile["theta"], chosen), 3),
                    "weak_concept_hit": int(target in set(chosen["expected_concepts"])),
                    "concept_count": len(chosen["expected_concepts"]),
                })

    metrics: dict[str, Any] = {}
    for policy in POLICIES:
        sub = [r for r in rows if r["policy"] == policy]
        metrics[policy] = {
            "trials": len(sub),
            "mean_candidate_count": round(statistics.mean(r["candidate_count"] for r in sub), 2),
            "weak_concept_coverage": round(statistics.mean(r["weak_concept_hit"] for r in sub), 3),
            "difficulty_hit_rate_0_5": round(statistics.mean(r["difficulty_hit_0_5"] for r in sub), 3),
            "difficulty_hit_rate_0_75": round(statistics.mean(r["difficulty_hit_0_75"] for r in sub), 3),
            "difficulty_match_error": round(statistics.mean(r["difficulty_error"] for r in sub), 3),
            "mean_item_information": round(statistics.mean(r["item_information"] for r in sub), 3),
        }

    return rows, metrics


def write_markdown(metrics: dict[str, Any]) -> None:
    path = OUT / "irt_sensitivity_summary.md"
    with path.open("w", encoding="utf-8") as f:
        f.write("# IRT Sensitivity Analysis\n\n")
        f.write("This experiment fixes the target weak concept first, then compares item-selection policies within the same concept-specific candidate pools.\n\n")
        f.write("| Policy | Trials | Weak cov. | Hit@0.5 | Hit@0.75 | Diff. error | Mean info |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for policy in POLICIES:
            m = metrics[policy]
            f.write(
                f"| {policy} | {m['trials']} | {m['weak_concept_coverage']:.3f} | "
                f"{m['difficulty_hit_rate_0_5']:.3f} | {m['difficulty_hit_rate_0_75']:.3f} | "
                f"{m['difficulty_match_error']:.3f} | {m['mean_item_information']:.3f} |\n"
            )


def main() -> int:
    rows, metrics = run()
    save_csv(OUT / "irt_sensitivity_rows.csv", rows)
    save_json(OUT / "irt_sensitivity_metrics.json", metrics)
    write_markdown(metrics)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"\nSaved rows to {OUT / 'irt_sensitivity_rows.csv'}")
    print(f"Saved metrics to {OUT / 'irt_sensitivity_metrics.json'}")
    print(f"Saved summary to {OUT / 'irt_sensitivity_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
