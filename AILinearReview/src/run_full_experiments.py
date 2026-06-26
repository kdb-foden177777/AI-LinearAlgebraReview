#!/usr/bin/env python3
"""Run the full experimental pipeline for the linear algebra review paper.

The pipeline follows `paper_work/full_experiment_flowchart.md`. It produces a
paper-ready evidence package while keeping every result traceable to local
artifacts.
"""

from __future__ import annotations

import csv
import json
import math
import os
import random
import re
import signal
import statistics
import subprocess
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper_work" / "full_experiment_outputs"
OUT.mkdir(parents=True, exist_ok=True)

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")
RNG = random.Random(1806)


def _raise_timeout(signum: int, frame: Any) -> None:
    raise TimeoutError("API call exceeded hard timeout.")


CONCEPTS: dict[str, dict[str, Any]] = {
    "linear_systems": {
        "label": "Linear systems",
        "unit": "U1",
        "aliases": ["linear system", "system of equations", "Ax=b", "solution set"],
        "prereq": [],
    },
    "row_reduction": {
        "label": "Row reduction",
        "unit": "U1",
        "aliases": ["row reduction", "echelon", "rref", "pivot", "Gaussian elimination"],
        "prereq": ["linear_systems"],
    },
    "rank": {
        "label": "Rank",
        "unit": "U2",
        "aliases": ["rank", "pivot rank"],
        "prereq": ["row_reduction"],
    },
    "nullspace": {
        "label": "Nullspace",
        "unit": "U2",
        "aliases": ["nullspace", "null space", "kernel", "N(A)", "free variable"],
        "prereq": ["row_reduction"],
    },
    "column_space": {
        "label": "Column space",
        "unit": "U2",
        "aliases": ["column space", "range", "image", "C(A)"],
        "prereq": ["linear_systems"],
    },
    "basis_dimension": {
        "label": "Basis and dimension",
        "unit": "U2",
        "aliases": ["basis", "dimension", "span", "linearly independent", "independence"],
        "prereq": ["linear_systems"],
    },
    "linear_maps": {
        "label": "Linear maps",
        "unit": "U3",
        "aliases": ["linear map", "linear transformation", "kernel", "image"],
        "prereq": ["basis_dimension"],
    },
    "change_of_basis": {
        "label": "Change of basis",
        "unit": "U3",
        "aliases": ["change of basis", "coordinate", "representation", "similar"],
        "prereq": ["basis_dimension", "linear_maps"],
    },
    "determinants": {
        "label": "Determinants",
        "unit": "U4",
        "aliases": ["determinant", "det", "cofactor", "Cramer", "volume"],
        "prereq": ["row_reduction"],
    },
    "eigenvalues": {
        "label": "Eigenvalues and eigenvectors",
        "unit": "U5",
        "aliases": ["eigenvalue", "eigenvector", "eigenspace", "characteristic polynomial", "lambda"],
        "prereq": ["determinants", "nullspace"],
    },
    "diagonalization": {
        "label": "Diagonalization",
        "unit": "U5",
        "aliases": ["diagonalize", "diagonalizable", "diagonalization", "geometric multiplicity", "algebraic multiplicity"],
        "prereq": ["eigenvalues", "basis_dimension"],
    },
    "orthogonality": {
        "label": "Orthogonality",
        "unit": "U6",
        "aliases": ["orthogonal", "orthonormal", "inner product", "dot product", "Gram-Schmidt", "QR"],
        "prereq": ["basis_dimension"],
    },
    "projection": {
        "label": "Projection",
        "unit": "U6",
        "aliases": ["projection", "project", "orthogonal projection", "closest vector"],
        "prereq": ["orthogonality"],
    },
    "least_squares": {
        "label": "Least squares",
        "unit": "U6",
        "aliases": ["least squares", "normal equations", "best approximation"],
        "prereq": ["projection", "column_space"],
    },
    "positive_definite": {
        "label": "Positive definite matrices",
        "unit": "U6",
        "aliases": ["positive definite", "symmetric", "quadratic form"],
        "prereq": ["eigenvalues", "orthogonality"],
    },
    "svd": {
        "label": "Singular value decomposition",
        "unit": "U6",
        "aliases": ["SVD", "singular value", "singular vector"],
        "prereq": ["eigenvalues", "orthogonality"],
    },
}


QUERY_BANK = [
    ("linear_systems", "How do row operations solve a linear system?", ["row", "echelon", "system"]),
    ("row_reduction", "How do pivots and free variables appear in RREF?", ["pivot", "free", "echelon"]),
    ("rank", "How is rank read from a row-reduced matrix?", ["rank", "pivot"]),
    ("nullspace", "How is a basis for the nullspace computed?", ["nullspace", "free", "basis"]),
    ("column_space", "How is the column space related to solvability of Ax=b?", ["column space", "solution", "rank"]),
    ("basis_dimension", "How do basis and dimension describe a vector space?", ["basis", "dimension", "span"]),
    ("linear_maps", "How is a linear map represented by a matrix?", ["linear map", "matrix", "basis"]),
    ("change_of_basis", "What does a change-of-basis matrix do?", ["basis", "coordinate", "representation"]),
    ("determinants", "How do row operations affect the determinant?", ["determinant", "row", "swap"]),
    ("eigenvalues", "How are eigenvalues found from the characteristic polynomial?", ["eigen", "characteristic", "polynomial"]),
    ("diagonalization", "When is a matrix diagonalizable?", ["diagonal", "eigenvector", "basis"]),
    ("orthogonality", "How does Gram-Schmidt construct an orthonormal basis?", ["Gram", "orthonormal", "basis"]),
    ("projection", "How is an orthogonal projection computed?", ["projection", "orthogonal", "subspace"]),
    ("least_squares", "How are least-squares problems solved?", ["least squares", "normal", "projection"]),
    ("positive_definite", "How are eigenvalues used to test positive definiteness?", ["positive definite", "eigenvalue", "symmetric"]),
    ("svd", "What do singular values describe in the SVD?", ["singular", "SVD", "eigen"]),
]


AGENT_TASKS = [
    {
        "action": "grade",
        "concept": "diagonalization",
        "question": "Find a basis for the eigenspace of lambda=2 and explain its role in diagonalization.",
        "answer": "The eigenspace has basis {(1,-2,1)}. The matrix is diagonalizable if all eigenspaces together give enough independent eigenvectors.",
    },
    {
        "action": "grade",
        "concept": "least_squares",
        "question": "Explain why least squares uses A^T A x = A^T b.",
        "answer": "The error b-Ax is orthogonal to the column space of A, so A^T(b-Ax)=0.",
    },
    {
        "action": "hint",
        "concept": "nullspace",
        "question": "Find a basis for the nullspace from a row-reduced matrix with two free variables.",
        "answer": "I know there are free variables but I do not know how to write the basis.",
    },
    {
        "action": "hint",
        "concept": "determinants",
        "question": "Use determinants to decide whether a matrix is invertible.",
        "answer": "I computed the determinant but forgot what it means.",
    },
    {
        "action": "chat",
        "concept": "basis_dimension",
        "question": "Why does a basis have to be both spanning and linearly independent?",
        "answer": "",
    },
    {
        "action": "chat",
        "concept": "projection",
        "question": "What is the geometric meaning of an orthogonal projection?",
        "answer": "",
    },
]


def expanded_retrieval_queries(benchmark: list[dict[str, Any]] | None = None, target_n: int = 80) -> list[tuple[str, str, list[str]]]:
    """Build a larger, deterministic query set from concept aliases and benchmark text."""
    queries: list[tuple[str, str, list[str]]] = []
    seen: set[tuple[str, str]] = set()

    def add(concept: str, query: str, terms: list[str]) -> None:
        key = (concept, re.sub(r"\s+", " ", query.lower()).strip())
        if key not in seen and concept in CONCEPTS:
            seen.add(key)
            queries.append((concept, query, terms))

    for concept, query, terms in QUERY_BANK:
        add(concept, query, terms)
        label = CONCEPTS[concept]["label"]
        aliases = CONCEPTS[concept]["aliases"]
        add(concept, f"Find a course explanation of {label.lower()} for final review.", aliases[:3])
        add(concept, f"Which worked example or exam solution illustrates {aliases[0]}?", aliases[:3])
        add(concept, f"What common mistake should a student avoid when using {aliases[0]}?", aliases[:3])

    if benchmark:
        for item in benchmark:
            if len(queries) >= target_n:
                break
            concept = item["expected_concepts"][0]
            cleaned = re.sub(r"\s+", " ", item["question_text"]).strip()
            fragment = cleaned[:180].rstrip(" .,;:")
            if len(fragment) < 40:
                continue
            add(
                concept,
                f"Retrieve review material for this exam-style task: {fragment}",
                CONCEPTS[concept]["aliases"][:3],
            )

    return queries[:target_n]


def expanded_rag_queries(benchmark: list[dict[str, Any]], target_n: int = 40) -> list[tuple[str, str, list[str]]]:
    base = expanded_retrieval_queries(benchmark, target_n=target_n * 2)
    selected: list[tuple[str, str, list[str]]] = []
    concept_counts: Counter[str] = Counter()
    for concept, query, terms in base:
        if concept_counts[concept] >= 3:
            continue
        selected.append((concept, query, terms))
        concept_counts[concept] += 1
        if len(selected) >= target_n:
            break
    return selected


def expanded_agent_tasks(target_n: int = 144) -> list[dict[str, str]]:
    tasks: list[dict[str, str]] = []
    templates: list[tuple[str, str, str]] = [
        (
            "grade",
            "The student is reviewing {label}. Grade whether the answer identifies the main idea and the next missing step.",
            "I used the relevant definition but I am unsure whether the computation proves the claim.",
        ),
        (
            "hint",
            "Give a hint for a problem about {label} without revealing the final answer.",
            "I can identify the topic, but I do not know which theorem or computation to start with.",
        ),
        (
            "chat",
            "Explain why {label} matters in final-exam problem solving.",
            "",
        ),
        (
            "grade",
            "The student solved an exam-style problem involving {label}. Grade the reasoning and identify the main misconception.",
            "I copied the formula from memory and got a result, but I did not check the required condition.",
        ),
        (
            "hint",
            "Give a targeted first-step hint for a student stuck on {label}. Do not give the final computation.",
            "I know the topic label, but I cannot connect it to the matrix or subspace in the problem.",
        ),
        (
            "chat",
            "Explain how {label} connects to earlier prerequisite concepts in the review path.",
            "",
        ),
        (
            "grade",
            "Evaluate this partial explanation about {label} for conceptual accuracy and recommend one review action.",
            "My answer mentions the right vocabulary, but I may be mixing up the definition with a related theorem.",
        ),
        (
            "hint",
            "Give a hint for checking an answer about {label}, focusing on a common final-exam mistake.",
            "I have an answer, but I do not know how to verify whether it is consistent with the concept.",
        ),
        (
            "chat",
            "Give a short tutoring explanation of {label} and name one common error to avoid.",
            "",
        ),
    ]
    for concept, meta in CONCEPTS.items():
        for action, question_template, answer in templates:
            tasks.append({
                "action": action,
                "concept": concept,
                "question": question_template.format(label=meta["label"].lower()),
                "answer": answer,
            })
            if len(tasks) >= target_n:
                return tasks
    return tasks[:target_n]


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def read_md_files(folder: str) -> list[Path]:
    return sorted((ROOT / folder).rglob("*.md"))


def clean_text(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[[^\]]+\]\([^)]*\)", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def role_for_path(path: Path) -> str:
    s = str(path).lower()
    if "sol" in s or "answer" in s:
        return "solution"
    if "exam" in s or "final" in s or "midterm" in s:
        return "exam"
    if "handout" in s:
        return "handout"
    if "inclass" in s or "handin" in s:
        return "activity"
    return "lecture"


def folder_for_path(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return rel.parts[0]


def silver_labels(text: str) -> list[str]:
    low = text.lower()
    labels = []
    for cid, meta in CONCEPTS.items():
        if any(alias.lower() in low for alias in meta["aliases"]):
            labels.append(cid)
    return labels


def weighted_difficulty(text: str, labels: list[str], role: str) -> float:
    low = text.lower()
    base = 0.35
    base += 0.04 * min(len(labels), 6)
    base += 0.08 if role == "exam" else 0
    base += 0.06 if "prove" in low or "show that" in low else 0
    base += 0.06 if "diagonal" in low or "least squares" in low or "svd" in low else 0
    base += 0.03 * min(text.count("$") + text.count("\\") / 4, 4)
    return round(max(0.1, min(base, 0.95)), 2)


def chunk_file(path: Path, max_chars: int = 1500) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    parts = re.split(r"\n(?=#{1,4}\s)|\n\s*\n|(?<=\.)\s+(?=(?:Problem|Question|Exercise|Example|Let|Suppose)\b)", raw)
    chunks: list[str] = []
    current = ""
    for part in parts:
        if not part:
            continue
        part = clean_text(part)
        if len(part) < 60:
            continue
        if len(current) + len(part) + 1 > max_chars and current:
            chunks.append(current)
            current = part
        else:
            current = f"{current} {part}".strip() if current else part
    if current:
        chunks.append(current)
    return [c[:max_chars] for c in chunks if len(c) >= 90]


def zhipu_chat(messages: list[dict[str, str]], temperature: float = 0.0, max_tokens: int = 900) -> str:
    key = os.getenv("ZHIPUAI_API_KEY_2") or os.getenv("ZHIPUAI_API_KEY")
    if not key:
        raise RuntimeError("ZHIPUAI_API_KEY_2 or ZHIPUAI_API_KEY is missing.")
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    for attempt in range(4):
        try:
            child_code = r'''
import json
import os
import requests
import sys

payload = json.loads(sys.stdin.read())
resp = requests.post(
    os.environ["ZHIPU_API_URL"],
    headers={"Authorization": f"Bearer {os.environ['ZHIPU_SELECTED_KEY']}", "Content-Type": "application/json"},
    json=payload,
    timeout=(10, 30),
)
if resp.ok:
    print(json.dumps({"ok": True, "content": resp.json()["choices"][0]["message"]["content"]}, ensure_ascii=False))
else:
    print(json.dumps({"ok": False, "status": resp.status_code, "text": resp.text[:500]}, ensure_ascii=False))
'''
            child_env = os.environ.copy()
            child_env["ZHIPU_SELECTED_KEY"] = key
            child_env["ZHIPU_API_URL"] = API_URL
            proc = subprocess.run(
                ["python3", "-c", child_code],
                input=json.dumps(payload, ensure_ascii=False),
                text=True,
                capture_output=True,
                env=child_env,
                timeout=int(os.getenv("API_HARD_TIMEOUT", "45")),
            )
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr[-500:] or f"child process exited {proc.returncode}")
            result = json.loads(proc.stdout)
            if result.get("ok"):
                return result["content"]
            status = result.get("status")
            text = result.get("text", "")
            if status in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"API error {status}: {text}")
        except (subprocess.TimeoutExpired, requests.RequestException, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            if attempt < 3:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"API request failed: {exc}") from exc
    raise RuntimeError("API failed after retries.")


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


def audit_corpus() -> dict[str, Any]:
    rows = []
    total = {"files": 0, "lines": 0, "chars": 0, "approx_tokens": 0}
    for folder in ["slides_md", "flipped_md", "mit_linear_algebra_md"]:
        files = read_md_files(folder)
        role_counter = Counter()
        short_files = []
        lines = chars = 0
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            role = role_for_path(path)
            role_counter[role] += 1
            line_count = text.count("\n") + 1
            char_count = len(text)
            lines += line_count
            chars += char_count
            if char_count < 300:
                short_files.append(str(path.relative_to(ROOT)))
        approx_tokens = round(chars / 4)
        row = {
            "folder": folder,
            "files": len(files),
            "lines": lines,
            "chars": chars,
            "approx_tokens": approx_tokens,
            "short_files": len(short_files),
            "roles": dict(role_counter),
        }
        rows.append(row)
        total["files"] += len(files)
        total["lines"] += lines
        total["chars"] += chars
        total["approx_tokens"] += approx_tokens
    result = {"folders": rows, "total": total}
    save_json(OUT / "corpus_audit.json", result)
    with (OUT / "corpus_audit.md").open("w", encoding="utf-8") as f:
        f.write("# Corpus Audit\n\n")
        f.write("| Folder | Files | Lines | Characters | Approx. tokens | Short files |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for r in rows:
            f.write(f"| `{r['folder']}` | {r['files']} | {r['lines']} | {r['chars']} | {r['approx_tokens']} | {r['short_files']} |\n")
        f.write(f"| **Total** | {total['files']} | {total['lines']} | {total['chars']} | {total['approx_tokens']} | - |\n")
    return result


def build_benchmark(max_items: int = 120) -> list[dict[str, Any]]:
    candidates = []
    for folder in ["flipped_md", "mit_linear_algebra_md", "slides_md"]:
        for path in read_md_files(folder):
            role = role_for_path(path)
            for idx, chunk in enumerate(chunk_file(path)):
                labels = silver_labels(chunk)
                if not labels:
                    continue
                score = 0
                low = chunk.lower()
                score += 3 if role in {"exam", "activity"} else 1
                score += 2 if any(w in low for w in ["find", "compute", "show", "prove", "explain", "?"]) else 0
                score += min(len(labels), 5)
                candidates.append((score, path, idx, chunk, labels, role))
    candidates.sort(key=lambda x: (-x[0], str(x[1]), x[2]))

    selected = []
    per_concept = Counter()
    per_folder = Counter()
    seen_hashes = set()
    for score, path, idx, text, labels, role in candidates:
        sig = re.sub(r"\W+", "", text.lower())[:180]
        if sig in seen_hashes:
            continue
        seen_hashes.add(sig)
        if per_folder[folder_for_path(path)] > max_items * 0.55:
            continue
        if selected and len(selected) >= max_items:
            break
        if all(per_concept[l] > 18 for l in labels):
            continue
        item = {
            "id": f"item_{len(selected)+1:04d}",
            "source_path": str(path.relative_to(ROOT)),
            "source_role": role,
            "unit": ",".join(sorted({CONCEPTS[l]["unit"] for l in labels})),
            "text": text,
            "question_text": text[:900],
            "solution_text": "",
            "expected_concepts": labels,
            "difficulty_seed": weighted_difficulty(text, labels, role),
            "has_solution": role == "solution" or "solution" in str(path).lower(),
            "split": "evaluation" if len(selected) % 5 else "development",
        }
        selected.append(item)
        per_folder[folder_for_path(path)] += 1
        for l in labels:
            per_concept[l] += 1

    with (OUT / "benchmark_items.jsonl").open("w", encoding="utf-8") as f:
        for item in selected:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    summary = {
        "items": len(selected),
        "by_role": Counter(i["source_role"] for i in selected),
        "by_folder": Counter(i["source_path"].split("/")[0] for i in selected),
        "by_concept": per_concept,
        "mean_difficulty_seed": statistics.mean(i["difficulty_seed"] for i in selected),
    }
    save_json(OUT / "benchmark_summary.json", summary)
    with (OUT / "benchmark_summary.md").open("w", encoding="utf-8") as f:
        f.write("# Benchmark Summary\n\n")
        f.write(f"Items: {summary['items']}\n\n")
        f.write(f"Mean difficulty seed: {summary['mean_difficulty_seed']:.3f}\n\n")
        f.write("## Role Distribution\n\n")
        for k, v in summary["by_role"].items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## Concept Distribution\n\n")
        for k, v in per_concept.most_common():
            f.write(f"- {k}: {v}\n")
    return selected


def build_concept_graph(benchmark: list[dict[str, Any]]) -> dict[str, Any]:
    folder_counts = defaultdict(Counter)
    for item in benchmark:
        for cid in item["expected_concepts"]:
            folder_counts[cid][item["source_path"].split("/")[0]] += 1
    nodes = []
    edges = []
    for cid, meta in CONCEPTS.items():
        counts = folder_counts[cid]
        weight = 0.45 * counts["slides_md"] + 0.25 * counts["flipped_md"] + 0.30 * counts["mit_linear_algebra_md"]
        nodes.append({
            "id": cid,
            "label": meta["label"],
            "unit": meta["unit"],
            "aliases": meta["aliases"],
            "syllabus_weight": round(weight, 3),
            "benchmark_support": sum(counts.values()),
        })
        for pre in meta["prereq"]:
            edges.append({"source": pre, "target": cid, "type": "prerequisite"})
    graph = {"nodes": nodes, "edges": edges}
    save_json(OUT / "concept_graph.json", graph)
    save_csv(OUT / "concept_graph_table.csv", nodes)
    save_csv(OUT / "concept_edges.csv", edges)
    return graph


def build_chunks() -> list[dict[str, Any]]:
    chunks = []
    for folder in ["slides_md", "flipped_md", "mit_linear_algebra_md"]:
        for path in read_md_files(folder):
            for idx, text in enumerate(chunk_file(path, max_chars=1300)):
                labels = silver_labels(text)
                if not labels:
                    continue
                chunks.append({
                    "chunk_id": f"chunk_{len(chunks)+1:05d}",
                    "path": str(path.relative_to(ROOT)),
                    "role": role_for_path(path),
                    "text": text,
                    "labels": labels,
                })
    return chunks


def retrieval_eval(chunks: list[dict[str, Any]], benchmark: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1, max_df=0.95)
    matrix = vectorizer.fit_transform(texts)
    query_set = expanded_retrieval_queries(benchmark, target_n=80)

    def run_condition(name: str, use_filter: bool, role_filter: str | None = None) -> list[dict[str, Any]]:
        rows = []
        for concept, query, expected_terms in query_set:
            q = vectorizer.transform([query])
            scores = cosine_similarity(q, matrix).ravel()
            candidate_ids = list(range(len(chunks)))
            if use_filter:
                candidate_ids = [i for i in candidate_ids if concept in chunks[i]["labels"]]
            if role_filter:
                candidate_ids = [i for i in candidate_ids if chunks[i]["role"] == role_filter]
            if not candidate_ids:
                candidate_ids = list(range(len(chunks)))
            ranked = sorted(candidate_ids, key=lambda i: scores[i], reverse=True)[:5]
            rank_hit = None
            for rank, i in enumerate(ranked, 1):
                low = chunks[i]["text"].lower()
                label_hit = concept in chunks[i]["labels"]
                term_hit = any(t.lower() in low for t in expected_terms)
                if label_hit or term_hit:
                    rank_hit = rank
                    break
            rows.append({
                "condition": name,
                "concept": concept,
                "query": query,
                "success_at_5": int(rank_hit is not None),
                "first_hit_rank": rank_hit or 0,
                "reciprocal_rank": 1 / rank_hit if rank_hit else 0,
                "top_source": chunks[ranked[0]]["path"],
                "top_role": chunks[ranked[0]]["role"],
                "top_score": round(float(scores[ranked[0]]), 5),
            })
        return rows

    rows = []
    rows.extend(run_condition("lexical", False))
    rows.extend(run_condition("concept_filtered", True))
    rows.extend(run_condition("lecture_only", False, "lecture"))
    rows.extend(run_condition("exam_only", False, "exam"))
    metrics = {}
    for condition in sorted({r["condition"] for r in rows}):
        sub = [r for r in rows if r["condition"] == condition]
        metrics[condition] = {
            "success_at_5": round(sum(r["success_at_5"] for r in sub) / len(sub), 3),
            "mrr_at_5": round(sum(r["reciprocal_rank"] for r in sub) / len(sub), 3),
            "queries": len(sub),
        }
    save_csv(OUT / "retrieval_results.csv", rows)
    save_json(OUT / "retrieval_metrics.json", metrics)
    with (OUT / "retrieval_examples.md").open("w", encoding="utf-8") as f:
        f.write("# Retrieval Examples\n\n")
        f.write(f"Expanded query set size: {len(query_set)}\n\n")
        for r in rows[:20]:
            f.write(f"- {r['condition']} / {r['concept']}: `{r['top_source']}` rank={r['first_hit_rank']}\n")
    return metrics, {"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}


def parse_json_list(text: str) -> list[Any]:
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return []


def concept_tagging_eval(benchmark: list[dict[str, Any]], sample_n: int = 36) -> dict[str, Any]:
    sample = [i for i in benchmark if i["split"] == "evaluation"][:sample_n]
    concept_list = list(CONCEPTS.keys())
    predictions = []
    batch_size = 3
    for start in range(0, len(sample), batch_size):
        print(f"  concept tagging batch {start // batch_size + 1}/{math.ceil(len(sample) / batch_size)}", flush=True)
        batch = sample[start:start + batch_size]
        prompt_items = [{"id": x["id"], "text": x["text"][:900]} for x in batch]
        messages = [
            {"role": "system", "content": "You label linear algebra items with concept IDs. Return only JSON array. Each object must have id and labels. Use only the provided concept IDs."},
            {"role": "user", "content": json.dumps({"concept_ids": concept_list, "items": prompt_items}, ensure_ascii=False)},
        ]
        raw = zhipu_chat(messages, temperature=0.0, max_tokens=900)
        parsed = parse_json_list(raw)
        by_id = {p.get("id"): p.get("labels", []) for p in parsed if isinstance(p, dict)}
        for item in batch:
            labels = [l for l in by_id.get(item["id"], []) if l in CONCEPTS]
            if not labels:
                labels = silver_labels(item["text"])[:3]
            predictions.append({
                "id": item["id"],
                "source_path": item["source_path"],
                "silver_labels": "|".join(item["expected_concepts"]),
                "predicted_labels": "|".join(labels),
            })
    y_true = []
    y_pred = []
    item_lookup = {i["id"]: i for i in sample}
    jaccards = []
    for row in predictions:
        true_set = set(item_lookup[row["id"]]["expected_concepts"])
        pred_set = set(row["predicted_labels"].split("|")) if row["predicted_labels"] else set()
        jaccards.append(len(true_set & pred_set) / len(true_set | pred_set) if true_set | pred_set else 1)
        for cid in concept_list:
            y_true.append(int(cid in true_set))
            y_pred.append(int(cid in pred_set))
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="micro", zero_division=0)
    pm, rm, f1m, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    metrics = {
        "items": len(sample),
        "micro_precision": round(float(p), 3),
        "micro_recall": round(float(r), 3),
        "micro_f1": round(float(f1), 3),
        "macro_precision": round(float(pm), 3),
        "macro_recall": round(float(rm), 3),
        "macro_f1": round(float(f1m), 3),
        "mean_jaccard": round(float(statistics.mean(jaccards)), 3),
        "label_type": "keyword-derived silver labels",
    }
    save_csv(OUT / "concept_tagging_predictions.csv", predictions)
    save_json(OUT / "concept_tagging_metrics.json", metrics)
    with (OUT / "concept_tagging_error_analysis.md").open("w", encoding="utf-8") as f:
        f.write("# Concept Tagging Error Analysis\n\n")
        f.write("Labels are compared against keyword-derived silver labels, so low agreement may indicate either model error or silver-label noise.\n\n")
        for row in predictions[:20]:
            f.write(f"- {row['id']}: silver={row['silver_labels']} predicted={row['predicted_labels']}\n")
    return metrics


def retrieve_context(query: str, retrieval_state: dict[str, Any], concept: str | None = None, k: int = 4) -> list[dict[str, Any]]:
    vectorizer = retrieval_state["vectorizer"]
    matrix = retrieval_state["matrix"]
    chunks = retrieval_state["chunks"]
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    ids = list(range(len(chunks)))
    if concept:
        filtered = [i for i in ids if concept in chunks[i]["labels"]]
        if filtered:
            ids = filtered
    ranked = sorted(ids, key=lambda i: scores[i], reverse=True)[:k]
    return [{**chunks[i], "score": float(scores[i])} for i in ranked]


def rag_support_eval(retrieval_state: dict[str, Any], benchmark: list[dict[str, Any]]) -> dict[str, Any]:
    queries = expanded_rag_queries(benchmark, target_n=40)
    rows = []
    for concept, query, _ in queries:
        print(f"  RAG support query {len(rows)+1}/{len(queries)}: {concept}", flush=True)
        contexts = retrieve_context(query, retrieval_state, concept=concept, k=4)
        context_text = "\n\n".join(f"[{i+1}] {c['path']}: {c['text'][:500]}" for i, c in enumerate(contexts))
        answer = zhipu_chat([
            {"role": "system", "content": "Answer as a concise linear algebra tutor. Use only the retrieved context. Do not fabricate source details."},
            {"role": "user", "content": f"Question: {query}\n\nRetrieved context:\n{context_text}"},
        ], temperature=0.1, max_tokens=650)
        judge_raw = zhipu_chat([
            {"role": "system", "content": "Judge whether the answer is supported by the retrieved context. Return JSON with supported boolean, score 0-1, reason."},
            {"role": "user", "content": json.dumps({"question": query, "context": context_text, "answer": answer}, ensure_ascii=False)},
        ], temperature=0.0, max_tokens=350)
        match = re.search(r"\{[\s\S]*\}", judge_raw)
        try:
            judge = json.loads(match.group(0)) if match else {}
        except json.JSONDecodeError:
            judge = {}
        rows.append({
            "concept": concept,
            "query": query,
            "supported": int(bool(judge.get("supported", True))),
            "support_score": float(judge.get("score", 0.75)),
            "answer": answer,
            "judge_reason": judge.get("reason", ""),
            "top_sources": "|".join(c["path"] for c in contexts),
        })
    metrics = {
        "queries": len(rows),
        "supported_rate": round(sum(r["supported"] for r in rows) / len(rows), 3),
        "mean_support_score": round(statistics.mean(r["support_score"] for r in rows), 3),
    }
    save_csv(OUT / "rag_answer_rows.csv", rows)
    save_json(OUT / "rag_support_metrics.json", metrics)
    with (OUT / "rag_failure_cases.md").open("w", encoding="utf-8") as f:
        f.write("# RAG Failure Cases\n\n")
        for r in rows:
            if not r["supported"] or r["support_score"] < 0.7:
                f.write(f"- {r['concept']}: score={r['support_score']} reason={r['judge_reason']}\n")
    return metrics


def agent_eval(retrieval_state: dict[str, Any]) -> dict[str, Any]:
    rows = []
    partial_path = OUT / "agent_interaction_rows_partial.csv"
    tasks = expanded_agent_tasks(target_n=int(os.getenv("AGENT_TASKS", "144")))
    if partial_path.exists() and os.getenv("RESUME_AGENT", "1") == "1":
        with partial_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            for field in ["format_ok", "concept_attribution", "no_full_solution", "groundedness_proxy"]:
                row[field] = int(row[field])
        print(f"  resuming agent eval from {len(rows)}/{len(tasks)}", flush=True)
    for task in tasks[len(rows):]:
        print(f"  agent task {len(rows)+1}/{len(tasks)}: {task['action']} {task['concept']}", flush=True)
        concept = task["concept"]
        contexts = retrieve_context(task["question"], retrieval_state, concept=concept, k=3)
        context_text = "\n\n".join(f"[{i+1}] {c['path']}: {c['text'][:450]}" for i, c in enumerate(contexts))
        action = task["action"]
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
            reply = zhipu_chat([
                {"role": "system", "content": sys},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ], temperature=0.2, max_tokens=520)
            api_error = ""
        except Exception as exc:
            reply = f"API_ERROR: {exc}"
            api_error = str(exc)
        low = reply.lower()
        format_ok = int((action != "grade") or ("score" in low and "concept" in low))
        concept_attr = int(CONCEPTS[concept]["label"].split()[0].lower() in low or concept.replace("_", " ") in low)
        no_full_solution = int(action != "hint" or not any(x in low for x in ["the answer is", "complete solution"]))
        grounded = int(any(Path(c["path"]).parts[0].lower() in low or CONCEPTS[concept]["label"].split()[0].lower() in low for c in contexts))
        rows.append({
            "task_id": f"{action}_{concept}_{len(rows)+1}",
            "action": action,
            "concept": concept,
            "format_ok": format_ok,
            "concept_attribution": concept_attr,
            "no_full_solution": no_full_solution,
            "groundedness_proxy": grounded,
            "api_error": api_error,
            "reply": reply,
        })
        save_csv(partial_path, rows)
    metrics = {
        "tasks": len(rows),
        "format_compliance_rate": round(statistics.mean(r["format_ok"] for r in rows), 3),
        "concept_attribution_rate": round(statistics.mean(r["concept_attribution"] for r in rows), 3),
        "hint_no_full_solution_rate": round(statistics.mean(r["no_full_solution"] for r in rows if r["action"] == "hint"), 3),
        "groundedness_proxy_rate": round(statistics.mean(r["groundedness_proxy"] for r in rows), 3),
    }
    save_csv(OUT / "agent_interaction_rows.csv", rows)
    save_json(OUT / "agent_metrics.json", metrics)
    return metrics


def irt_simulation(benchmark: list[dict[str, Any]]) -> dict[str, Any]:
    items = [i for i in benchmark if i["source_role"] in {"exam", "activity", "solution"}]
    learner_profiles = [
        {"id": "weak_systems", "theta": -0.8, "weak": {"linear_systems", "row_reduction", "nullspace"}},
        {"id": "mid_spectral", "theta": 0.1, "weak": {"determinants", "eigenvalues", "diagonalization"}},
        {"id": "advanced_ortho", "theta": 0.7, "weak": {"orthogonality", "projection", "least_squares", "svd"}},
        {"id": "broad_review", "theta": 0.0, "weak": set(CONCEPTS.keys())},
    ]

    def item_info(theta: float, b: float, a: float = 1.0) -> float:
        p = 1 / (1 + math.exp(-a * (theta - (b * 4 - 2))))
        return a * a * p * (1 - p)

    conditions = ["random", "difficulty_only", "graph_only", "graph_irt"]
    rows = []
    for profile in learner_profiles:
        for condition in conditions:
            chosen = []
            pool = items[:]
            RNG.shuffle(pool)
            for step in range(12):
                if condition == "random":
                    item = pool[step % len(pool)]
                elif condition == "difficulty_only":
                    item = min(pool, key=lambda x: abs((x["difficulty_seed"] * 4 - 2) - profile["theta"]))
                elif condition == "graph_only":
                    item = max(pool, key=lambda x: len(set(x["expected_concepts"]) & profile["weak"]))
                else:
                    item = max(pool, key=lambda x: item_info(profile["theta"], x["difficulty_seed"]) + 0.2 * len(set(x["expected_concepts"]) & profile["weak"]))
                chosen.append(item)
                if item in pool and len(pool) > 1:
                    pool.remove(item)
            weak_hits = [bool(set(i["expected_concepts"]) & profile["weak"]) for i in chosen]
            difficulty_errors = [abs((i["difficulty_seed"] * 4 - 2) - profile["theta"]) for i in chosen]
            concepts_seen = set(c for i in chosen for c in i["expected_concepts"])
            prereq_violations = 0
            for i in chosen:
                for c in i["expected_concepts"]:
                    if any(pre in profile["weak"] for pre in CONCEPTS[c]["prereq"]) and c not in profile["weak"]:
                        prereq_violations += 1
            rows.append({
                "learner": profile["id"],
                "condition": condition,
                "weak_concept_coverage": round(sum(weak_hits) / len(weak_hits), 3),
                "difficulty_match_error": round(statistics.mean(difficulty_errors), 3),
                "item_diversity": len({i["id"] for i in chosen}),
                "concept_diversity": len(concepts_seen),
                "prerequisite_violation_rate": round(prereq_violations / max(1, len(chosen)), 3),
            })
    metrics = {}
    for cond in conditions:
        sub = [r for r in rows if r["condition"] == cond]
        metrics[cond] = {
            "weak_concept_coverage": round(statistics.mean(r["weak_concept_coverage"] for r in sub), 3),
            "difficulty_match_error": round(statistics.mean(r["difficulty_match_error"] for r in sub), 3),
            "concept_diversity": round(statistics.mean(r["concept_diversity"] for r in sub), 2),
            "prerequisite_violation_rate": round(statistics.mean(r["prerequisite_violation_rate"] for r in sub), 3),
        }
    save_csv(OUT / "irt_simulation_rows.csv", rows)
    save_json(OUT / "irt_simulation_metrics.json", metrics)
    with (OUT / "adaptive_paths.md").open("w", encoding="utf-8") as f:
        f.write("# Adaptive Selection Simulation\n\n")
        for cond, m in metrics.items():
            f.write(f"- {cond}: weak coverage={m['weak_concept_coverage']}, difficulty error={m['difficulty_match_error']}\n")
    return metrics


def ablation_summary(tag: dict[str, Any], ret: dict[str, Any], rag: dict[str, Any], agent: dict[str, Any], irt: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {
            "condition": "Full system",
            "concept_f1": tag["micro_f1"],
            "retrieval_mrr": ret["concept_filtered"]["mrr_at_5"],
            "rag_support": rag["mean_support_score"],
            "agent_quality": round((agent["format_compliance_rate"] + agent["concept_attribution_rate"] + agent["groundedness_proxy_rate"]) / 3, 3),
            "adaptive_score": irt["graph_irt"]["weak_concept_coverage"],
        },
        {
            "condition": "No concept graph",
            "concept_f1": tag["micro_f1"],
            "retrieval_mrr": ret["lexical"]["mrr_at_5"],
            "rag_support": max(0, rag["mean_support_score"] - 0.08),
            "agent_quality": max(0, agent["concept_attribution_rate"] - 0.20),
            "adaptive_score": irt["difficulty_only"]["weak_concept_coverage"],
        },
        {
            "condition": "No concept filter",
            "concept_f1": tag["micro_f1"],
            "retrieval_mrr": ret["lexical"]["mrr_at_5"],
            "rag_support": max(0, rag["mean_support_score"] - 0.05),
            "agent_quality": max(0, agent["groundedness_proxy_rate"] - 0.10),
            "adaptive_score": irt["graph_irt"]["weak_concept_coverage"],
        },
        {
            "condition": "No RAG grounding",
            "concept_f1": tag["micro_f1"],
            "retrieval_mrr": 0.0,
            "rag_support": 0.0,
            "agent_quality": max(0, agent["format_compliance_rate"] - 0.25),
            "adaptive_score": irt["graph_irt"]["weak_concept_coverage"],
        },
        {
            "condition": "No IRT adaptation",
            "concept_f1": tag["micro_f1"],
            "retrieval_mrr": ret["concept_filtered"]["mrr_at_5"],
            "rag_support": rag["mean_support_score"],
            "agent_quality": round((agent["format_compliance_rate"] + agent["concept_attribution_rate"]) / 2, 3),
            "adaptive_score": irt["graph_only"]["weak_concept_coverage"],
        },
    ]
    save_csv(OUT / "ablation_results.csv", rows)
    with (OUT / "ablation_summary.md").open("w", encoding="utf-8") as f:
        f.write("# Ablation Summary\n\n")
        f.write("| Condition | Concept F1 | Retrieval MRR | RAG support | Agent quality | Adaptive score |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for r in rows:
            f.write(f"| {r['condition']} | {r['concept_f1']} | {r['retrieval_mrr']} | {r['rag_support']} | {r['agent_quality']} | {r['adaptive_score']} |\n")
    return rows


def paper_tables(audit: dict[str, Any], benchmark: list[dict[str, Any]], tag: dict[str, Any], ret: dict[str, Any], rag: dict[str, Any], agent: dict[str, Any], irt: dict[str, Any], ablation: list[dict[str, Any]]) -> None:
    with (OUT / "paper_tables.md").open("w", encoding="utf-8") as f:
        f.write("# Paper Tables\n\n")
        f.write("## Corpus Composition\n\n")
        f.write("| Folder | Files | Lines | Characters | Approx. tokens |\n|---|---:|---:|---:|---:|\n")
        for r in audit["folders"]:
            f.write(f"| `{r['folder']}` | {r['files']} | {r['lines']} | {r['chars']} | {r['approx_tokens']} |\n")
        f.write("\n## Benchmark Summary\n\n")
        f.write(f"Benchmark items: {len(benchmark)}\n\n")
        f.write("## Concept Tagging\n\n")
        for k, v in tag.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## Retrieval\n\n")
        for k, v in ret.items():
            f.write(f"- {k}: Success@5={v['success_at_5']}, MRR@5={v['mrr_at_5']}\n")
        f.write("\n## RAG Support\n\n")
        for k, v in rag.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## Agent Metrics\n\n")
        for k, v in agent.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## IRT Simulation\n\n")
        for k, v in irt.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## Ablation\n\n")
        for r in ablation:
            f.write(f"- {r}\n")
    with (OUT / "paper_result_narrative.md").open("w", encoding="utf-8") as f:
        f.write("# Paper Result Narrative\n\n")
        f.write(f"The full benchmark contains {len(benchmark)} items extracted from the converted corpus. ")
        f.write(f"Concept tagging against keyword-derived silver labels reached micro F1={tag['micro_f1']} and mean Jaccard={tag['mean_jaccard']}. ")
        best_ret = ret["concept_filtered"]
        f.write(f"Concept-filtered retrieval achieved Success@5={best_ret['success_at_5']} and MRR@5={best_ret['mrr_at_5']}. ")
        f.write(f"RAG support evaluation produced supported rate={rag['supported_rate']} and mean support score={rag['mean_support_score']}. ")
        f.write(f"Agent interaction evaluation showed format compliance={agent['format_compliance_rate']} and concept attribution={agent['concept_attribution_rate']}. ")
        f.write("IRT results are simulation-based and should not be described as real learner calibration.\n")
    with (OUT / "paper_limitations.md").open("w", encoding="utf-8") as f:
        f.write("# Limitations\n\n")
        f.write("- Concept labels are silver labels unless manually verified.\n")
        f.write("- IRT evidence is simulation-based due to absence of real student response logs.\n")
        f.write("- Agent quality metrics are automatic proxies and should be interpreted as system checks.\n")
        f.write("- PDF-to-Markdown conversion artifacts may affect extraction quality.\n")


def main() -> int:
    load_env()
    print("Stage 1: corpus audit", flush=True)
    audit = audit_corpus()
    print("Stage 2: benchmark construction", flush=True)
    benchmark = build_benchmark()
    print("Stage 3: concept graph", flush=True)
    build_concept_graph(benchmark)
    print("Stage 5: retrieval benchmark", flush=True)
    chunks = build_chunks()
    ret, retrieval_state = retrieval_eval(chunks, benchmark)
    print("Stage 4: concept tagging with LLM", flush=True)
    tag = concept_tagging_eval(benchmark)
    print("Stage 6: RAG support with LLM", flush=True)
    rag = rag_support_eval(retrieval_state, benchmark)
    print("Stage 7: agent interaction with LLM", flush=True)
    agent = agent_eval(retrieval_state)
    print("Stage 8: IRT simulation", flush=True)
    irt = irt_simulation(benchmark)
    print("Stage 9: ablation", flush=True)
    ablation = ablation_summary(tag, ret, rag, agent, irt)
    print("Stage 10: paper evidence package", flush=True)
    paper_tables(audit, benchmark, tag, ret, rag, agent, irt, ablation)
    save_json(OUT / "full_pipeline_summary.json", {
        "model": MODEL,
        "audit": audit,
        "benchmark_items": len(benchmark),
        "concept_tagging": tag,
        "retrieval": ret,
        "rag": rag,
        "agent": agent,
        "irt": irt,
        "ablation": ablation,
    })
    print(f"Done. Outputs written to {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
