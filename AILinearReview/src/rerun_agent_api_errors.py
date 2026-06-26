#!/usr/bin/env python3
"""Rerun only failed agent-interaction API calls.

This script repairs `agent_interaction_rows.csv` without rerunning completed
agent tasks. It keeps the original 144-task design and rewrites the metrics
from the repaired row-level file.
"""

from __future__ import annotations

import csv
import json
import os
import statistics
import time
from pathlib import Path

import requests

import run_full_experiments as exp


OUT = exp.OUT
ROWS_PATH = OUT / "agent_interaction_rows.csv"
PARTIAL_PATH = OUT / "agent_interaction_rows_partial.csv"
METRICS_PATH = OUT / "agent_metrics.json"


def bit(value: object) -> int:
    return 1 if str(value).strip() == "1" else 0


def save_rows(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "task_id",
        "action",
        "concept",
        "format_ok",
        "concept_attribution",
        "no_full_solution",
        "groundedness_proxy",
        "api_error",
        "reply",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def recompute_metrics(rows: list[dict[str, object]]) -> dict[str, object]:
    completed = [r for r in rows if not str(r.get("api_error", "")).strip()]
    errors = len(rows) - len(completed)
    metrics = {
        "tasks": len(rows),
        "completed_tasks": len(completed),
        "api_error_count": errors,
        "completed_response_rate": round(len(completed) / len(rows), 3) if rows else 0,
        "format_compliance_rate": round(statistics.mean(bit(r.get("format_ok")) for r in completed), 3) if completed else 0,
        "concept_attribution_rate": round(statistics.mean(bit(r.get("concept_attribution")) for r in completed), 3) if completed else 0,
        "hint_no_full_solution_rate": round(
            statistics.mean(bit(r.get("no_full_solution")) for r in completed if r.get("action") == "hint"), 3
        ) if any(r.get("action") == "hint" for r in completed) else 0,
        "groundedness_proxy_rate": round(statistics.mean(bit(r.get("groundedness_proxy")) for r in completed), 3) if completed else 0,
        "by_action": {},
    }
    for action in ["grade", "hint", "chat"]:
        sub = [r for r in rows if r.get("action") == action]
        sub_completed = [r for r in sub if not str(r.get("api_error", "")).strip()]
        metrics["by_action"][action] = {
            "tasks": len(sub),
            "completed_tasks": len(sub_completed),
            "api_error_count": len(sub) - len(sub_completed),
            "completed_response_rate": round(len(sub_completed) / len(sub), 3) if sub else 0,
            "concept_attribution_rate": round(statistics.mean(bit(r.get("concept_attribution")) for r in sub_completed), 3) if sub_completed else 0,
            "groundedness_proxy_rate": round(statistics.mean(bit(r.get("groundedness_proxy")) for r in sub_completed), 3) if sub_completed else 0,
        }
        if action == "grade":
            metrics["by_action"][action]["rubric_format_rate"] = round(
                statistics.mean(bit(r.get("format_ok")) for r in sub_completed), 3
            ) if sub_completed else 0
        if action == "hint":
            metrics["by_action"][action]["no_full_solution_rate"] = round(
                statistics.mean(bit(r.get("no_full_solution")) for r in sub_completed), 3
            ) if sub_completed else 0
    return metrics


def zhipu_chat_long(messages: list[dict[str, str]], temperature: float = 0.0, max_tokens: int = 420) -> str:
    key = os.getenv("ZHIPUAI_API_KEY_2") or os.getenv("ZHIPUAI_API_KEY")
    if not key:
        raise RuntimeError("ZHIPUAI_API_KEY_2 or ZHIPUAI_API_KEY is missing.")
    payload = {
        "model": exp.MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            resp = requests.post(
                exp.API_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
                timeout=(15, 120),
            )
            if resp.ok:
                return resp.json()["choices"][0]["message"]["content"]
            if resp.status_code in {429, 500, 502, 503, 504} and attempt < 4:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"API error {resp.status_code}: {resp.text[:500]}")
        except Exception as exc:
            last_error = exc
            if attempt < 4:
                time.sleep(2**attempt)
                continue
    raise RuntimeError(f"API request failed: {last_error}")


def main() -> int:
    exp.load_env()
    if not ROWS_PATH.exists():
        raise FileNotFoundError(f"Missing {ROWS_PATH}")

    with ROWS_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    failed_indices = [i for i, row in enumerate(rows) if str(row.get("api_error", "")).strip()]
    print(f"Found {len(failed_indices)} failed agent rows.")
    if not failed_indices:
        metrics = recompute_metrics(rows)
        METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        print(f"No failed rows remain. Metrics refreshed at {METRICS_PATH}.")
        return 0

    chunks = exp.build_chunks()
    texts = [c["text"] for c in chunks]
    vectorizer = exp.TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, max_df=0.95)
    matrix = vectorizer.fit_transform(texts)
    retrieval_state = {"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}

    for n, idx in enumerate(failed_indices, 1):
        row = rows[idx]
        action = str(row["action"])
        concept = str(row["concept"])
        task_no = idx + 1
        task = exp.expanded_agent_tasks(target_n=144)[idx]
        print(f"Rerun {n}/{len(failed_indices)}: row {task_no}, {action}, {concept}", flush=True)

        contexts = exp.retrieve_context(task["question"], retrieval_state, concept=concept, k=3)
        context_text = "\n\n".join(f"[{i+1}] {c['path']}: {c['text'][:450]}" for i, c in enumerate(contexts))
        if action == "grade":
            sys = "You are a grading agent. Return concise feedback with Score, Correct steps, Missing or weak steps, Concept attribution, Recommended next action."
        elif action == "hint":
            sys = "You are a hint agent. Give a useful hint without revealing the full solution."
        else:
            sys = "You are a dialogue tutor. Answer directly and connect the explanation to the current concept."
        prompt = {
            "action": action,
            "concept": concept,
            "question": task["question"],
            "student_answer": task["answer"],
            "retrieved_context": context_text,
        }
        try:
            reply = zhipu_chat_long([
                {"role": "system", "content": sys},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ], temperature=0.2, max_tokens=420)
            api_error = ""
        except Exception as exc:
            reply = f"API_ERROR: {exc}"
            api_error = str(exc)

        low = reply.lower()
        format_ok = int((action != "grade") or ("score" in low and "concept" in low))
        concept_attr = int(exp.CONCEPTS[concept]["label"].split()[0].lower() in low or concept.replace("_", " ") in low)
        no_full_solution = int(action != "hint" or not any(x in low for x in ["the answer is", "complete solution"]))
        grounded = int(any(Path(c["path"]).parts[0].lower() in low or exp.CONCEPTS[concept]["label"].split()[0].lower() in low for c in contexts))

        rows[idx].update({
            "format_ok": format_ok,
            "concept_attribution": concept_attr,
            "no_full_solution": no_full_solution,
            "groundedness_proxy": grounded,
            "api_error": api_error,
            "reply": reply,
        })
        save_rows(ROWS_PATH, rows)
        save_rows(PARTIAL_PATH, rows)

    metrics = recompute_metrics(rows)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    remaining = sum(1 for row in rows if str(row.get("api_error", "")).strip())
    print(f"Done. Remaining failed rows: {remaining}")
    print(f"Updated {ROWS_PATH}")
    print(f"Updated {METRICS_PATH}")
    return 0 if remaining == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
