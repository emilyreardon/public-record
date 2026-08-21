#!/usr/bin/env python3
"""
ai_server.py
============
Local FastAPI server for the Public Record installation.

Endpoints:
  GET  /health      → {"status": "ok", "docs": N}
  POST /echo        → nearest corpus doc to visitor's response
  GET  /clusters    → today's submission themes (via Ollama + Supabase)

Set AI_URL in submit.html to 'http://<this-machine-ip>:8000' to activate.

Usage:
    python3 ai_server.py [--port 8000] [--host 0.0.0.0]

Requirements: see requirements_ai.txt
Run setup first: python3 chunk_and_embed.py
"""

import argparse
import json
import os
import re
import sqlite3
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import chromadb
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Config ────────────────────────────────────────────────────────────────────

DB_DIR          = Path(__file__).parent / "chroma_db"
SQLITE_PATH     = Path(__file__).parent / "submissions.db"
COLLECTION_NAME = "corpus"
OLLAMA_URL      = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL     = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL       = os.getenv("LLM_MODEL",  "olmo3-instruct")       # ollama pull olmo3-instruct

# Cluster cache: recompute at most every N seconds
CLUSTER_TTL     = 120


# ── SQLite setup ──────────────────────────────────────────────────────────────

def init_db():
    con = sqlite3.connect(SQLITE_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at        TEXT    DEFAULT (datetime('now')),
            doc_id            INTEGER,
            doc_title         TEXT,
            response_text     TEXT,
            submit_template   TEXT,
            first_name        TEXT,
            installation_name TEXT,
            visitor_zip       TEXT,
            consented         INTEGER DEFAULT 1,
            ui_language       TEXT
        )
    """)
    con.commit()
    con.close()

init_db()

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(title="Public Record AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # installation is local network; fine to open
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── ChromaDB ──────────────────────────────────────────────────────────────────

_client:     Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection]       = None


def get_collection() -> chromadb.Collection:
    global _client, _collection
    if _collection is None:
        if not DB_DIR.exists():
            raise RuntimeError(
                f"ChromaDB not found at {DB_DIR}. Run: python3 chunk_and_embed.py"
            )
        _client     = chromadb.PersistentClient(path=str(DB_DIR))
        _collection = _client.get_collection(COLLECTION_NAME)
    return _collection


# ── Ollama helpers ────────────────────────────────────────────────────────────

def embed_text(text: str) -> list[float]:
    resp = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": [text]},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "embeddings" in data:
        return data["embeddings"][0]
    return data["embedding"]


def llm_complete(prompt: str, max_tokens: int = 200) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model":  LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.3},
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


# ── Cluster cache ─────────────────────────────────────────────────────────────

_cluster_cache: dict = {"ts": 0, "clusters": []}


def _submissions_today() -> list[str]:
    """Fetch today's responses from local SQLite. Returns list of response strings."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        con = sqlite3.connect(SQLITE_PATH)
        rows = con.execute(
            "SELECT response_text FROM submissions WHERE created_at >= ? AND response_text IS NOT NULL",
            (today + "T00:00:00",)
        ).fetchall()
        con.close()
        return [r[0] for r in rows if r[0]]
    except Exception as e:
        print(f"[clusters] SQLite fetch error: {e}")
        return []


def _theme_from_llm(responses: list[str]) -> list[dict]:
    """Ask the LLM to group responses into 3-5 short theme labels."""
    if not responses:
        return []

    sample = responses[:40]  # cap for speed
    joined = "\n".join(f"- {r[:120]}" for r in sample)

    prompt = (
        "You are helping analyze responses from a civic art installation. "
        "People responded to prompts about U.S. founding documents and civil rights.\n\n"
        "Responses:\n"
        f"{joined}\n\n"
        "Group these into 3 to 5 short theme labels (2-4 words each). "
        "For each theme, count how many responses fit it. "
        "Reply ONLY with JSON: [{\"theme\": \"...\", \"count\": N}, ...]\n"
        "Do not explain. Only JSON."
    )

    try:
        raw = llm_complete(prompt, max_tokens=300)
        # Extract JSON array from response
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if m:
            clusters = json.loads(m.group(0))
            # Validate shape
            return [
                {"theme": str(c["theme"]), "count": int(c["count"])}
                for c in clusters
                if "theme" in c and "count" in c
            ]
    except Exception as e:
        print(f"[clusters] LLM parse error: {e} | raw: {raw[:200]}")

    return []


def _keyword_clusters(responses: list[str]) -> list[dict]:
    """Fallback: simple keyword frequency when LLM is unavailable."""
    THEMES = {
        "democracy & voting":  ["vote", "voting", "election", "democracy", "ballot", "suffrage"],
        "free speech":         ["speech", "say", "silence", "voice", "expression", "speak"],
        "equality & rights":   ["equal", "right", "fair", "justice", "freedom", "liberty"],
        "immigration":         ["immigrant", "border", "citizenship", "asylum", "deport"],
        "health & body":       ["health", "medical", "body", "care", "abortion", "disability"],
        "environment":         ["climate", "environment", "land", "water", "earth", "nature"],
        "education":           ["school", "education", "learn", "teach", "student", "college"],
        "economic justice":    ["wage", "work", "housing", "homeless", "money", "poor", "wealth"],
    }
    counts: Counter = Counter()
    for resp in responses:
        lower = resp.lower()
        for theme, keywords in THEMES.items():
            if any(kw in lower for kw in keywords):
                counts[theme] += 1

    top = counts.most_common(5)
    return [{"theme": t, "count": c} for t, c in top if c > 0]


def get_clusters(force: bool = False) -> list[dict]:
    global _cluster_cache
    now = time.time()
    if not force and (now - _cluster_cache["ts"]) < CLUSTER_TTL:
        return _cluster_cache["clusters"]

    responses = _submissions_today()
    if not responses:
        _cluster_cache = {"ts": now, "clusters": []}
        return []

    # Try LLM first, fall back to keywords
    clusters = _theme_from_llm(responses)
    if not clusters:
        clusters = _keyword_clusters(responses)

    # Sort by count desc
    clusters.sort(key=lambda c: -c["count"])
    _cluster_cache = {"ts": now, "clusters": clusters}
    return clusters


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    try:
        col = get_collection()
        count = col.count()
    except Exception as e:
        return {"status": "degraded", "error": str(e), "docs": 0}
    try:
        con = sqlite3.connect(SQLITE_PATH)
        submissions = con.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        con.close()
    except Exception:
        submissions = -1
    return {"status": "ok", "docs": count, "submissions": submissions, "model": EMBED_MODEL}


class SubmitRequest(BaseModel):
    doc_id:            Optional[int]  = None
    doc_title:         Optional[str]  = None
    response_text:     str
    submit_template:   Optional[str]  = None
    first_name:        Optional[str]  = None
    installation_name: Optional[str]  = None
    visitor_zip:       Optional[str]  = None
    consented:         bool           = True
    ui_language:       Optional[str]  = "en"


@app.post("/submit")
def submit(req: SubmitRequest):
    if not req.response_text.strip():
        raise HTTPException(400, "response_text is required")
    try:
        con = sqlite3.connect(SQLITE_PATH)
        con.execute(
            """INSERT INTO submissions
               (doc_id, doc_title, response_text, submit_template,
                first_name, installation_name, visitor_zip, consented, ui_language)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (req.doc_id, req.doc_title, req.response_text, req.submit_template,
             req.first_name, req.installation_name, req.visitor_zip,
             1 if req.consented else 0, req.ui_language)
        )
        con.commit()
        con.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, f"Database error: {e}")


class EchoRequest(BaseModel):
    text:   str
    doc_id: Optional[int] = None   # exclude the source doc from results


@app.post("/echo")
def echo(req: EchoRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "text is required")

    try:
        vec = embed_text(text)
    except Exception as e:
        raise HTTPException(503, f"Embedding model unavailable: {e}")

    try:
        col = get_collection()
    except Exception as e:
        raise HTTPException(503, str(e))

    # Exclude the doc the visitor was responding to
    where = None
    if req.doc_id:
        where = {"corpus_id": {"$ne": req.doc_id}}

    results = col.query(
        query_embeddings=[vec],
        n_results=3,
        where=where,
        include=["metadatas", "documents", "distances"],
    )

    if not results["ids"] or not results["ids"][0]:
        raise HTTPException(404, "No corpus docs found")

    # Return the closest match
    meta     = results["metadatas"][0][0]
    doc_text = results["documents"][0][0]
    distance = results["distances"][0][0]

    # Pull a short clause from the doc text (first sentence ≤ 160 chars)
    sentences = re.split(r"(?<=[.!?])\s+", doc_text)
    clause    = next((s for s in sentences if 20 < len(s) < 200), sentences[0][:160])

    # Ask the LLM to generate a soulful, document-anchored echo.
    # We deliberately do NOT give the LLM the visitor's exact words —
    # only the matched document — so garbage input can't corrupt the output.
    generated_echo = None
    try:
        echo_prompt = (
            "You are writing 2 sentences for a visitor at a civic art installation about American democracy.\n\n"
            f"Their response connected to this document: {meta.get('title', '')}\n"
            f"A key passage: \"{clause}\"\n\n"
            "Write exactly 2 sentences:\n"
            "1. What this document achieved and how ordinary people made it happen. Be specific and human.\n"
            "2. Tell the visitor this document is hanging in the installation. Invite them to find it, scan its QR code, and discover what question it still has not answered.\n\n"
            "Rules: No em dashes. Plain language. Short sentences. Do not use the word 'civic'. "
            "Do not quote the passage. Make it feel personal and alive, not academic."
        )
        generated_echo = llm_complete(echo_prompt, max_tokens=150)
        # Strip any leading/trailing quotes the model might add
        generated_echo = generated_echo.strip('"').strip()
    except Exception as e:
        print(f"[echo] LLM generation failed: {e}")

    return {
        "match_id":       meta.get("corpus_id", -1),
        "match_title":    meta.get("title", ""),
        "match_clause":   clause,
        "generated_echo": generated_echo,
        "distance":       round(distance, 4),
    }


@app.get("/clusters")
def clusters(force: bool = False):
    data = get_clusters(force=force)
    return {"clusters": data, "cached_at": _cluster_cache["ts"]}


# ── Dev server ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    print(f"\n Public Record AI server")
    print(f" DB:      {DB_DIR}")
    print(f" Ollama:  {OLLAMA_URL}")
    print(f" Models:  embed={EMBED_MODEL}  llm={LLM_MODEL}")
    print(f" Listen:  http://{args.host}:{args.port}\n")

    uvicorn.run("ai_server:app", host=args.host, port=args.port, reload=False)
