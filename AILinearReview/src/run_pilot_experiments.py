#!/usr/bin/env python3
"""Run pilot experiments for the linear algebra adaptive review paper.

The experiments are intentionally small and reproducible. They are designed to
produce real numbers for a first manuscript draft without building a full
production learning system.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "paper_work" / "experiment_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


CONCEPTS = [
    "linear_systems",
    "row_reduction",
    "rank",
    "nullspace",
    "column_space",
    "basis_dimension",
    "linear_maps",
    "change_of_basis",
    "determinants",
    "eigenvalues",
    "diagonalization",
    "orthogonality",
    "projection",
    "least_squares",
    "positive_definite",
    "svd",
]

KEYWORD_LABELS = {
    "linear_systems": ["linear system", "Ax = b", "system of equations", "solve"],
    "row_reduction": ["row reduction", "echelon", "pivot", "Gauss", "elimination", "LU"],
    "rank": ["rank"],
    "nullspace": ["nullspace", "null space", "kernel", "N(A)"],
    "column_space": ["column space", "C(A)", "range", "image"],
    "basis_dimension": ["basis", "dimension", "span", "linearly independent"],
    "linear_maps": ["linear map", "linear transformation", "map", "transformation"],
    "change_of_basis": ["basis", "coordinate", "represent", "Rep", "change of basis"],
    "determinants": ["determinant", "det", "Cramer"],
    "eigenvalues": ["eigenvalue", "eigenvector", "characteristic", "lambda"],
    "diagonalization": ["diagonalize", "diagonalizable", "similar", "matrix powers"],
    "orthogonality": ["orthogonal", "orthonormal", "Gram", "QR"],
    "projection": ["projection", "project", "closest point", "distance"],
    "least_squares": ["least squares", "normal equations", "minimizing"],
    "positive_definite": ["positive definite", "negative definite", "symmetric"],
    "svd": ["SVD", "singular value", "singular values"],
}


RETRIEVAL_PROBES = [
    ("linear_systems", "How do row operations solve a linear system?", ["row", "echelon", "system"]),
    ("nullspace", "What is the nullspace of a matrix and how is it found?", ["nullspace", "free", "basis"]),
    ("column_space", "How is the column space related to solvability of Ax=b?", ["column space", "solution", "rank"]),
    ("basis_dimension", "How do basis and dimension describe a vector space?", ["basis", "dimension", "span"]),
    ("linear_maps", "How is a linear map represented by a matrix?", ["linear map", "basis", "matrix"]),
    ("determinants", "How do row operations affect the determinant?", ["determinant", "row", "swap"]),
    ("eigenvalues", "How are eigenvalues found from the characteristic polynomial?", ["eigen", "characteristic", "polynomial"]),
    ("diagonalization", "When is a matrix diagonalizable?", ["diagonal", "eigenvector", "basis"]),
    ("orthogonality", "How does Gram-Schmidt construct an orthonormal basis?", ["Gram", "orthonormal", "basis"]),
    ("projection", "How is an orthogonal projection computed?", ["projection", "orthogonal", "subspace"]),
    ("least_squares", "How are least squares problems solved?", ["least squares", "normal", "projection"]),
    ("svd", "What do singular values describe in the SVD?", ["singular", "SVD", "eigen"]),
]


TAGGING_FILES = [
    "mit_linear_algebra_md/fall2017/final/final.md",
    "mit_linear_algebra_md/spring2014/Final_s14_draft/Final_s14_draft.md",
    "mit_linear_algebra_md/spring2022/final/final.md",
    "mit_linear_algebra_md/fall2018/final/final.md",
    "flipped_md/handin/final/final.md",
    "flipped_md/handin/midterm/midterm.md",
]


RAG_QUERIES = [
    (
        "Explain why a low score on eigenvalue problems may indicate prerequisite gaps in determinants and nullspace solving.",
        ["eigen", "determinant", "nullspace", "characteristic"],
    ),
    (
        "Explain how a review system should remediate mistakes in least squares problems.",
        ["least squares", "projection", "normal equations", "orthogonal"],
    ),
    (
        "Explain how row reduction supports rank, nullspace, and column space reasoning.",
        ["row reduction", "rank", "nullspace", "column space", "pivot"],
    ),
]


def load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def zhipu_chat(messages: list[dict], temperature: float = 0.0, max_tokens: int = 512) -> str:
    key = os.getenv("ZHIPUAI_API_KEY")
    if not key:
        raise RuntimeError("ZHIPUAI_API_KEY is missing. Put it in .env.")
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    for attempt in range(4):
        try:
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
                timeout=(20, 60),
            )
        except requests.RequestException as exc:
            if attempt < 3:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"Zhipu API request failed after retries: {exc}") from exc
        if response.ok:
            return response.json()["choices"][0]["message"]["content"]
        if response.status_code in {429, 500, 502, 503, 504} and attempt < 3:
            time.sleep(2**attempt)
            continue
        raise RuntimeError(f"Zhipu API error {response.status_code}: {response.text[:500]}")
    raise RuntimeError("Zhipu API failed after retries")


def read_md_files(folder: str) -> list[Path]:
    return sorted((ROOT / folder).rglob("*.md"))


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(path: Path, max_chars: int = 1800) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    parts = re.split(r"\n(?=#{1,4}\s)|\n\s*\n", text)
    chunks = []
    current = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(current) + len(part) + 2 > max_chars and current:
            chunks.append(current)
            current = part
        else:
            current = (current + "\n\n" + part).strip() if current else part
    if current:
        chunks.append(current)
    return [
        {
            "path": str(path.relative_to(ROOT)),
            "chunk_id": i,
            "text": c[:max_chars],
        }
        for i, c in enumerate(chunks)
        if len(c) > 80
    ]


def build_corpus_chunks() -> list[dict]:
    chunks = []
    for folder in ["slides_md", "flipped_md"]:
        for path in read_md_files(folder):
            chunks.extend(chunk_text(path))
    return chunks


def corpus_stats() -> dict:
    folders = ["slides_md", "flipped_md", "mit_linear_algebra_md"]
    stats = {}
    for folder in folders:
        files = read_md_files(folder)
        line_count = 0
        char_count = 0
        for p in files:
            text = p.read_text(encoding="utf-8", errors="ignore")
            line_count += text.count("\n") + 1
            char_count += len(text)
        stats[folder] = {
            "files": len(files),
            "lines": line_count,
            "chars": char_count,
        }
    return stats


def run_retrieval(chunks: list[dict]) -> dict:
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    rows = []
    successes = 0
    mrr_total = 0.0
    for concept, query, expected in RETRIEVAL_PROBES:
        q_vec = vectorizer.transform([query])
        scores = cosine_similarity(q_vec, matrix).ravel()
        top_indices = scores.argsort()[::-1][:5]
        top_chunks = [chunks[i] for i in top_indices]
        expected_l = [e.lower() for e in expected]
        rank_hit = None
        for rank, c in enumerate(top_chunks, start=1):
            text_l = c["text"].lower()
            if any(e in text_l for e in expected_l):
                rank_hit = rank
                break
        success = rank_hit is not None
        successes += int(success)
        mrr_total += 1.0 / rank_hit if rank_hit else 0.0
        rows.append(
            {
                "concept": concept,
                "query": query,
                "success_at_5": success,
                "first_hit_rank": rank_hit,
                "top_source": top_chunks[0]["path"],
                "top_score": float(scores[top_indices[0]]),
            }
        )
    return {
        "rows": rows,
        "success_at_5": successes / len(RETRIEVAL_PROBES),
        "mrr_at_5": mrr_total / len(RETRIEVAL_PROBES),
    }


def weak_labels(text: str) -> list[str]:
    text_l = text.lower()
    labels = []
    for label, kws in KEYWORD_LABELS.items():
        if any(kw.lower() in text_l for kw in kws):
            labels.append(label)
    return labels[:4]


def extract_question_snippets(limit: int = 24) -> list[dict]:
    snippets = []
    split_re = re.compile(r"(?=\n(?:#{1,4}\s*)?(?:Problem\s+\d+|\d+\.\s|\-\s\*\*\d+\.))", re.I)
    for rel in TAGGING_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        parts = [normalize_space(p) for p in split_re.split("\n" + text)]
        for part in parts:
            if len(part) < 250:
                continue
            # Cut before explicit solution when possible.
            part = re.split(r"\bSolution:|\*\*Solution\*\*|#### Solution", part, flags=re.I)[0]
            part = part[:1400]
            labels = weak_labels(part)
            if not labels:
                continue
            snippets.append({"source": rel, "text": part, "weak_labels": labels})
            if len(snippets) >= limit:
                return snippets
    return snippets


def parse_json_list(response: str) -> list[str]:
    match = re.search(r"\[[\s\S]*?\]", response)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return [x for x in data if x in CONCEPTS]


def run_concept_tagging(snippets: list[dict]) -> dict:
    rows = []
    y_true = []
    y_pred = []
    for i, item in enumerate(snippets, start=1):
        print(f"[concept-tagging] {i}/{len(snippets)}", flush=True)
        prompt = (
            "You are labeling linear algebra exam questions for an adaptive review system.\n"
            f"Allowed labels: {', '.join(CONCEPTS)}.\n"
            "Return only a JSON array of 1 to 4 labels. Do not explain.\n\n"
            f"Question:\n{item['text']}"
        )
        response = zhipu_chat(
            [
                {"role": "system", "content": "You return compact JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=128,
        )
        pred = parse_json_list(response)
        if not pred:
            pred = weak_labels(response)
        rows.append(
            {
                "id": i,
                "source": item["source"],
                "weak_labels": item["weak_labels"],
                "predicted_labels": pred,
                "response": response,
            }
        )
        y_true.append([1 if c in item["weak_labels"] else 0 for c in CONCEPTS])
        y_pred.append([1 if c in pred else 0 for c in CONCEPTS])
        time.sleep(0.15)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="micro", zero_division=0
    )
    jaccards = []
    for row in rows:
        a = set(row["weak_labels"])
        b = set(row["predicted_labels"])
        if a or b:
            jaccards.append(len(a & b) / len(a | b))
    return {
        "rows": rows,
        "micro_precision": float(precision),
        "micro_recall": float(recall),
        "micro_f1": float(f1),
        "mean_jaccard": float(sum(jaccards) / len(jaccards)) if jaccards else 0.0,
    }


def run_rag_support(chunks: list[dict]) -> dict:
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    rows = []
    for i, (query, filters) in enumerate(RAG_QUERIES, start=1):
        print(f"[rag-support] {i}/{len(RAG_QUERIES)}", flush=True)
        scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
        filter_l = [f.lower() for f in filters]
        candidate_indices = [
            idx for idx, chunk in enumerate(chunks)
            if any(f in chunk["text"].lower() for f in filter_l)
        ]
        if not candidate_indices:
            candidate_indices = list(range(len(chunks)))
        top_indices = sorted(candidate_indices, key=lambda idx: scores[idx], reverse=True)[:3]
        ctx_parts = []
        sources = []
        for j, idx in enumerate(top_indices, start=1):
            chunk = chunks[idx]
            sources.append(chunk["path"])
            ctx_parts.append(f"[C{j}] Source: {chunk['path']}\n{chunk['text'][:1200]}")
        context = "\n\n".join(ctx_parts)
        answer = zhipu_chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You answer as a linear algebra tutoring-system designer. "
                        "Use only the provided context. Cite chunks as [C1], [C2], etc."
                    ),
                },
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
            temperature=0.2,
            max_tokens=260,
        )
        judge = zhipu_chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a strict evaluator. Return only JSON exactly like "
                        "{\"supported\": true, \"score\": 0.85}. "
                        "The score must be a number from 0 to 1."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Is the answer supported by the context? Penalize unsupported claims.\n\n"
                        f"Context:\n{context}\n\nAnswer:\n{answer}"
                    ),
                },
            ],
            temperature=0.0,
            max_tokens=128,
        )
        score = 0.0
        supported = False
        m = re.search(r"\{[\s\S]*\}", judge)
        if m:
            try:
                data = json.loads(m.group(0))
                supported = bool(data.get("supported", False))
                raw_score = data.get("score", 0.0)
                if isinstance(raw_score, dict):
                    raw_score = next((v for v in raw_score.values() if isinstance(v, (int, float))), 0.0)
                score = float(raw_score)
            except Exception:
                pass
        rows.append(
            {
                "id": i,
                "query": query,
                "sources": sources,
                "answer": answer,
                "judge": judge,
                "supported": supported,
                "support_score": score,
            }
        )
        time.sleep(0.15)
    return {
        "rows": rows,
        "supported_rate": sum(r["supported"] for r in rows) / len(rows),
        "mean_support_score": sum(r["support_score"] for r in rows) / len(rows),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary(results: dict) -> None:
    path = OUT_DIR / "experiment_summary.md"
    stats = results["corpus_stats"]
    retrieval = results["retrieval"]
    tagging = results["concept_tagging"]
    rag = results["rag_support"]
    path.write_text(
        f"""# Pilot Experiment Summary

Model used for LLM-based steps: `{MODEL}`.

## Corpus Characterization

| Folder | Files | Lines | Characters |
|---|---:|---:|---:|
| `slides_md` | {stats['slides_md']['files']} | {stats['slides_md']['lines']} | {stats['slides_md']['chars']} |
| `flipped_md` | {stats['flipped_md']['files']} | {stats['flipped_md']['lines']} | {stats['flipped_md']['chars']} |
| `mit_linear_algebra_md` | {stats['mit_linear_algebra_md']['files']} | {stats['mit_linear_algebra_md']['lines']} | {stats['mit_linear_algebra_md']['chars']} |

## Retrieval Pilot

TF-IDF retrieval was evaluated on {len(RETRIEVAL_PROBES)} concept-oriented probes.

| Metric | Value |
|---|---:|
| Success@5 | {retrieval['success_at_5']:.3f} |
| MRR@5 | {retrieval['mrr_at_5']:.3f} |

## Concept-Tagging Pilot

ZhipuAI labeled {len(tagging['rows'])} exam/exercise snippets. Scores are computed against weak keyword-derived silver labels.

| Metric | Value |
|---|---:|
| Micro precision | {tagging['micro_precision']:.3f} |
| Micro recall | {tagging['micro_recall']:.3f} |
| Micro F1 | {tagging['micro_f1']:.3f} |
| Mean Jaccard | {tagging['mean_jaccard']:.3f} |

## RAG Support Pilot

ZhipuAI generated context-grounded answers for {len(rag['rows'])} design queries, and a second model call judged support against retrieved chunks.

| Metric | Value |
|---|---:|
| Supported rate | {rag['supported_rate']:.3f} |
| Mean support score | {rag['mean_support_score']:.3f} |

## Notes

These are pilot experiments for a system manuscript, not final large-scale user studies. The concept-tagging labels are silver labels derived from keywords, so they should be reported as an automatic consistency check rather than as human-annotated ground truth.
""",
        encoding="utf-8",
    )


def main() -> None:
    load_env()
    print("[setup] building chunks", flush=True)
    chunks = build_corpus_chunks()
    stats = corpus_stats()
    print("[retrieval] running local retrieval benchmark", flush=True)
    retrieval = run_retrieval(chunks)
    snippets = extract_question_snippets(limit=12)
    print(f"[concept-tagging] extracted {len(snippets)} snippets", flush=True)
    tagging = run_concept_tagging(snippets)
    partial = {
        "model": MODEL,
        "corpus_stats": stats,
        "retrieval": retrieval,
        "concept_tagging": tagging,
    }
    (OUT_DIR / "pilot_partial_before_rag.json").write_text(
        json.dumps(partial, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    rag = run_rag_support(chunks)
    results = {
        "model": MODEL,
        "corpus_stats": stats,
        "retrieval": retrieval,
        "concept_tagging": tagging,
        "rag_support": rag,
    }
    (OUT_DIR / "pilot_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(OUT_DIR / "retrieval_rows.csv", retrieval["rows"])
    write_csv(OUT_DIR / "concept_tagging_rows.csv", tagging["rows"])
    write_csv(OUT_DIR / "rag_support_rows.csv", rag["rows"])
    write_summary(results)
    print(json.dumps({
        "retrieval_success_at_5": retrieval["success_at_5"],
        "tagging_micro_f1": tagging["micro_f1"],
        "rag_supported_rate": rag["supported_rate"],
        "outputs": str(OUT_DIR.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
