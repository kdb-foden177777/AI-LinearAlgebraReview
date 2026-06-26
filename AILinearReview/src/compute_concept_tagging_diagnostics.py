#!/usr/bin/env python3
"""Compute transparent diagnostics for concept-tagging evaluation."""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_work" / "full_experiment_outputs"


def split_labels(raw: str) -> set[str]:
    return {x for x in raw.split("|") if x}


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def save_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    pred_path = OUT / "concept_tagging_predictions_expanded.csv"
    metrics_path = OUT / "concept_tagging_diagnostics_expanded.json"
    item_path = OUT / "concept_tagging_item_diagnostics_expanded.csv"
    concept_path = OUT / "concept_tagging_per_concept_expanded.csv"
    md_path = OUT / "concept_tagging_diagnostics_expanded.md"
    if not pred_path.exists():
        pred_path = OUT / "concept_tagging_predictions.csv"
        metrics_path = OUT / "concept_tagging_diagnostics.json"
        item_path = OUT / "concept_tagging_item_diagnostics.csv"
        concept_path = OUT / "concept_tagging_per_concept.csv"
        md_path = OUT / "concept_tagging_diagnostics.md"
    with pred_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    item_rows = []
    concept_counts = Counter()
    concept_tp = Counter()
    concept_fp = Counter()
    concept_fn = Counter()

    for row in rows:
        if row.get("status", "ok") != "ok":
            continue
        silver = split_labels(row["silver_labels"])
        predicted = split_labels(row["predicted_labels"])
        inter = silver & predicted
        union = silver | predicted
        missing = silver - predicted
        extra = predicted - silver
        for c in union:
            concept_counts[c] += 1
            if c in silver and c in predicted:
                concept_tp[c] += 1
            elif c in predicted:
                concept_fp[c] += 1
            elif c in silver:
                concept_fn[c] += 1
        item_rows.append({
            "id": row["id"],
            "source_path": row["source_path"],
            "silver_count": len(silver),
            "predicted_count": len(predicted),
            "intersection_count": len(inter),
            "missing_count": len(missing),
            "extra_count": len(extra),
            "exact_match": int(silver == predicted),
            "under_label": int(len(predicted) < len(silver)),
            "over_label": int(len(predicted) > len(silver)),
            "jaccard": round(len(inter) / len(union), 3) if union else 1.0,
            "missing_labels": "|".join(sorted(missing)),
            "extra_labels": "|".join(sorted(extra)),
        })

    concept_rows = []
    for concept in sorted(concept_counts):
        tp = concept_tp[concept]
        fp = concept_fp[concept]
        fn = concept_fn[concept]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        concept_rows.append({
            "concept": concept,
            "support": tp + fn,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
        })

    metrics = {
        "items": len(rows),
        "mean_silver_labels_per_item": round(statistics.mean(r["silver_count"] for r in item_rows), 3),
        "mean_predicted_labels_per_item": round(statistics.mean(r["predicted_count"] for r in item_rows), 3),
        "mean_missing_labels_per_item": round(statistics.mean(r["missing_count"] for r in item_rows), 3),
        "mean_extra_labels_per_item": round(statistics.mean(r["extra_count"] for r in item_rows), 3),
        "exact_match_rate": round(statistics.mean(r["exact_match"] for r in item_rows), 3),
        "under_label_rate": round(statistics.mean(r["under_label"] for r in item_rows), 3),
        "over_label_rate": round(statistics.mean(r["over_label"] for r in item_rows), 3),
        "mean_jaccard_from_predictions": round(statistics.mean(r["jaccard"] for r in item_rows), 3),
    }

    save_json(metrics_path, metrics)
    save_csv(item_path, item_rows)
    save_csv(concept_path, concept_rows)
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Concept Tagging Diagnostics\n\n")
        f.write("| Metric | Value |\n|---|---:|\n")
        for k, v in metrics.items():
            f.write(f"| {k} | {v} |\n")
        f.write("\n## Per-concept metrics\n\n")
        f.write("| Concept | Support | Precision | Recall | F1 |\n|---|---:|---:|---:|---:|\n")
        for row in concept_rows:
            f.write(f"| {row['concept']} | {row['support']} | {row['precision']} | {row['recall']} | {row['f1']} |\n")
    print(f"Wrote concept-tagging diagnostics to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
