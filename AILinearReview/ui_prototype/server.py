#!/usr/bin/env python3
"""Local UI server for the adaptive linear algebra review prototype.

The browser never sees the API key. This server reads `.env`, serves the static
prototype, and exposes a small `/api/agent` endpoint backed by ZhipuAI.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import error, request


UI_DIR = Path(__file__).resolve().parent
ROOT = UI_DIR.parents[1]
ITEM_BANK_PATH = ROOT / "paper_work" / "full_experiment_outputs" / "benchmark_items.jsonl"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")


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


def zhipu_chat(messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int = 700) -> str:
    key = os.getenv("ZHIPUAI_API_KEY")
    if not key:
        raise RuntimeError("ZHIPUAI_API_KEY is missing. Put it in .env.")

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(3):
        req = request.Request(
            API_URL,
            data=data,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=45) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)["choices"][0]["message"]["content"]
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            if exc.code in {429, 500, 502, 503, 504} and attempt < 2:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"ZhipuAI error {exc.code}: {body[:500]}") from exc
        except error.URLError as exc:
            if attempt < 2:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"ZhipuAI request failed: {exc.reason}") from exc

    raise RuntimeError("ZhipuAI request failed after retries.")


def build_prompt(payload: dict[str, Any]) -> list[dict[str, str]]:
    action = payload.get("action", "chat")
    user_input = str(payload.get("input", "")).strip()
    item = payload.get("item") or {}
    learner_state = payload.get("learner_state") or {}

    item_text = {
        "title": item.get("title"),
        "concepts": item.get("concepts"),
        "difficulty": item.get("difficulty"),
        "path": item.get("path"),
        "evidence": item.get("evidence"),
        "question": item.get("questionHtml"),
    }

    if action == "grade":
        system = (
            "You are a rigorous linear algebra grading agent. You must answer in English. "
            "Grade the learner response against the current item. Ground feedback in the "
            "concept list, review path, and learner state. Do not invent exact source quotes."
        )
        task = (
            "Grade the student's answer to the current item. Use this format:\n"
            "Score: NN/100\n"
            "- Correct steps: ...\n"
            "- Missing or weak steps: ...\n"
            "- Concept attribution: ...\n"
            "- Recommended next action: ..."
        )
    elif action == "hint":
        system = (
            "You are a concise linear algebra hint agent. You must answer in English. "
            "Give a targeted hint without revealing the full solution unless explicitly asked. "
            "Ground the hint in the current item, concept list, and review path."
        )
        task = (
            "Give one targeted hint for the current item. Do not reveal the complete answer. "
            "Mention which concept the learner should focus on next."
        )
    else:
        system = (
            "You are a concise linear algebra dialogue tutor. You must answer in English. "
            "Answer the learner's question directly. Do not assign a score, do not grade, "
            "and do not use a grading rubric unless the learner explicitly asks for grading. "
            "Connect the explanation to the current item and review path when useful."
        )
        task = (
            "Answer the learner's question as a tutoring agent. Connect the answer to the "
            "current item and review path when relevant. Use one or two short paragraphs."
        )

    content = (
        f"Action: {action}\n\n"
        f"Task: {task}\n\n"
        f"Current item JSON:\n{json.dumps(item_text, ensure_ascii=False)}\n\n"
        f"Learner state JSON:\n{json.dumps(learner_state, ensure_ascii=False)}\n\n"
        f"Learner input:\n{user_input}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": content}]


CONCEPT_LABELS = {
    "linear_systems": "Linear systems",
    "row_reduction": "Row reduction",
    "rank": "Rank",
    "nullspace": "Nullspace computation",
    "column_space": "Column space",
    "basis_dimension": "Basis and dimension",
    "linear_maps": "Linear maps",
    "change_of_basis": "Change of basis",
    "determinants": "Determinants",
    "eigenvalues": "Eigenvalues",
    "diagonalization": "Diagonalization criterion",
    "orthogonality": "Orthogonality",
    "projection": "Orthogonal projection",
    "least_squares": "Least squares",
    "positive_definite": "Positive definite matrices",
    "svd": "SVD",
    "characteristic_polynomial": "Characteristic polynomial",
}


def load_item_bank(limit: int = 90) -> list[dict[str, Any]]:
    if not ITEM_BANK_PATH.exists():
        return []

    rows: list[dict[str, Any]] = []
    with ITEM_BANK_PATH.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    preferred = [
        row for row in rows
        if str(row.get("source_path", "")).startswith(("flipped_md/", "mit_linear_algebra_md/"))
        and row.get("source_role") in {"exam", "activity", "solution"}
        and len(str(row.get("question_text") or row.get("text") or "")) > 80
    ]
    preferred.sort(key=lambda row: (
        0 if str(row.get("source_path", "")).startswith("mit_linear_algebra_md/") else 1,
        row.get("id", ""),
    ))
    return [format_item(row) for row in preferred[:limit]]


def format_item(row: dict[str, Any]) -> dict[str, Any]:
    concepts = list(row.get("expected_concepts") or [])
    source_path = str(row.get("source_path", "unknown source"))
    role = str(row.get("source_role", "item")).title()
    title = make_title(row, concepts)
    question = clean_question(row.get("question_text") or row.get("text") or "")
    solution = clean_answer(row.get("solution_text") or "")
    path = review_path(concepts)
    evidence = [
        [source_path, evidence_sentence(source_path, concepts)],
        ["concept_graph", f"Active concept labels: {', '.join(CONCEPT_LABELS.get(c, c.replace('_', ' ')) for c in concepts[:5])}."],
    ]
    return {
        "id": row.get("id"),
        "source": f"{role} item",
        "title": title,
        "difficulty": round(float(row.get("difficulty_seed", 0.55)), 2),
        "concepts": concepts,
        "questionHtml": markdownish_to_html(question),
        "starterAnswer": solution,
        "path": path,
        "activePathIndex": min(1, max(0, len(path) - 1)),
        "evidence": evidence,
        "sourcePath": source_path,
        "sourceRole": row.get("source_role"),
    }


def make_title(row: dict[str, Any], concepts: list[str]) -> str:
    labels = [CONCEPT_LABELS.get(c, c.replace("_", " ").title()) for c in concepts[:2]]
    base = " and ".join(labels) if labels else "Linear Algebra Review"
    role = str(row.get("source_role", "item")).title()
    source = "MIT" if str(row.get("source_path", "")).startswith("mit_linear_algebra_md/") else "Flipped"
    return f"{source} {role}: {base}"


def clean_question(text: str, max_chars: int = 1400) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    text = text.replace(" - ", "\n- ")
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + " ..."
    return text


def clean_answer(text: str, max_chars: int = 900) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    if not text:
        return ""
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + " ..."
    return text


def markdownish_to_html(text: str) -> str:
    escaped = escape(text)
    lines = [line.strip() for line in escaped.splitlines() if line.strip()]
    if not lines:
        return "<p>No question text available.</p>"
    blocks = []
    bullets = []
    for line in lines:
        if line.startswith("- "):
            bullets.append(f"<li>{line[2:]}</li>")
        else:
            if bullets:
                blocks.append("<ul>" + "".join(bullets) + "</ul>")
                bullets = []
            blocks.append(f"<p>{line}</p>")
    if bullets:
        blocks.append("<ul>" + "".join(bullets) + "</ul>")
    return "\n".join(blocks)


def review_path(concepts: list[str]) -> list[str]:
    if not concepts:
        return ["Identify concept", "Retrieve evidence", "Attempt item", "Review feedback"]
    labels = [CONCEPT_LABELS.get(c, c.replace("_", " ").title()) for c in concepts]
    compact = []
    for label in labels:
        if label not in compact:
            compact.append(label)
    return compact[:4] if len(compact) >= 4 else compact + ["Retrieved example", "Follow-up practice"][: 4 - len(compact)]


def evidence_sentence(source_path: str, concepts: list[str]) -> str:
    source = "MIT final-exam material" if source_path.startswith("mit_linear_algebra_md/") else "Flipped-classroom material"
    labels = ", ".join(CONCEPT_LABELS.get(c, c.replace("_", " ")) for c in concepts[:3])
    return f"{source} linked to {labels or 'linear algebra review'}."


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self.send_json({"ok": True, "model": MODEL, "has_key": bool(os.getenv("ZHIPUAI_API_KEY"))})
            return
        if self.path.startswith("/api/items"):
            self.send_json({"items": load_item_bank()})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/agent":
            self.send_error(404, "Not found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body or "{}")
            reply = zhipu_chat(build_prompt(payload))
            self.send_json({"reply": reply, "score": "Agent", "confidence": 0.9, "model": MODEL})
        except Exception as exc:
            self.send_json({"error": str(exc)}, status=500)

    def send_json(self, data: dict[str, Any], status: int = 200) -> None:
        encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> int:
    load_env()
    port = int(os.getenv("UI_PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving UI at http://127.0.0.1:{port}")
    print(f"Agent model: {MODEL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
