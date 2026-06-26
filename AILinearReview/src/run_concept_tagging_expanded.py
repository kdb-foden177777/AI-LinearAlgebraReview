#!/usr/bin/env python3
"""Run a resumable expanded concept-tagging evaluation."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from sklearn.metrics import precision_recall_fscore_support

import run_full_experiments as exp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_work" / "full_experiment_outputs"
PRED_PATH = OUT / "concept_tagging_predictions_expanded.csv"
METRICS_PATH = OUT / "concept_tagging_metrics_expanded.json"


def load_benchmark() -> list[dict]:
    path = OUT / "benchmark_items.jsonl"
    if not path.exists():
        return exp.build_benchmark()
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_existing() -> list[dict]:
    if not PRED_PATH.exists():
        return []
    with PRED_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_rows(rows: list[dict]) -> None:
    fields = ["id", "source_path", "silver_labels", "predicted_labels", "status", "error"]
    with PRED_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_labels(raw: str, concept_ids: set[str]) -> list[str]:
    parsed = exp.parse_json_list(raw)
    if parsed and isinstance(parsed[0], dict):
        labels = parsed[0].get("labels", [])
    elif parsed and isinstance(parsed[0], str):
        labels = parsed
    else:
        labels = re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", raw)
    seen = []
    for label in labels:
        if label in concept_ids and label not in seen:
            seen.append(label)
    return seen


def compute_metrics(rows: list[dict], sample: list[dict]) -> dict:
    ok_rows = [r for r in rows if r["status"] == "ok"]
    item_lookup = {i["id"]: i for i in sample}
    concept_list = list(exp.CONCEPTS.keys())
    y_true = []
    y_pred = []
    jaccards = []
    for row in ok_rows:
        true_set = set(item_lookup[row["id"]]["expected_concepts"])
        pred_set = set(row["predicted_labels"].split("|")) if row["predicted_labels"] else set()
        jaccards.append(len(true_set & pred_set) / len(true_set | pred_set) if true_set | pred_set else 1)
        for cid in concept_list:
            y_true.append(int(cid in true_set))
            y_pred.append(int(cid in pred_set))
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="micro", zero_division=0)
    pm, rm, f1m, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    return {
        "target_items": len(sample),
        "completed_items": len(ok_rows),
        "api_error_items": len(rows) - len(ok_rows),
        "micro_precision": round(float(p), 3),
        "micro_recall": round(float(r), 3),
        "micro_f1": round(float(f1), 3),
        "macro_precision": round(float(pm), 3),
        "macro_recall": round(float(rm), 3),
        "macro_f1": round(float(f1m), 3),
        "mean_jaccard": round(sum(jaccards) / len(jaccards), 3) if jaccards else 0.0,
        "label_type": "keyword-derived silver labels",
    }


def main() -> int:
    exp.load_env()
    benchmark = load_benchmark()
    sample = [i for i in benchmark if i["split"] == "evaluation"][:80]
    concept_ids = set(exp.CONCEPTS.keys())
    rows = load_existing()
    done = {r["id"] for r in rows}
    for item in sample:
        if item["id"] in done:
            continue
        print(f"concept tagging {len(rows)+1}/{len(sample)}: {item['id']}", flush=True)
        messages = [
            {
                "role": "system",
                "content": (
                    "You label one linear algebra item with concept IDs. "
                    "Return only a JSON array with one object: "
                    "[{\"id\":\"...\",\"labels\":[...]}]. Use only the provided concept IDs."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "concept_ids": list(exp.CONCEPTS.keys()),
                    "item": {"id": item["id"], "text": item["text"][:650]},
                }, ensure_ascii=False),
            },
        ]
        try:
            raw = exp.zhipu_chat(messages, temperature=0.0, max_tokens=350)
            labels = parse_labels(raw, concept_ids)
            status = "ok"
            error = ""
        except Exception as exc:
            labels = []
            status = "api_error"
            error = str(exc)[:300]
        rows.append({
            "id": item["id"],
            "source_path": item["source_path"],
            "silver_labels": "|".join(item["expected_concepts"]),
            "predicted_labels": "|".join(labels),
            "status": status,
            "error": error,
        })
        save_rows(rows)

    metrics = compute_metrics(rows, sample)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
