#!/usr/bin/env python3
"""
chunk_and_embed.py
==================
Ingests all 137 Public Record corpus documents into ChromaDB,
using nomic-embed-text (via Ollama) for embeddings.

Run once before starting ai_server.py, and re-run if the corpus changes.

Usage:
    python3 chunk_and_embed.py [--corpus-dir ./public-record-corpus] [--db-dir ./chroma_db]

Requirements:
    pip install chromadb requests
    ollama pull nomic-embed-text
"""

import argparse
import json
import re
import sys
from pathlib import Path

import requests
import chromadb

# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_CORPUS_DIR = Path(__file__).parent / "public-record-corpus"
DEFAULT_DB_DIR     = Path(__file__).parent / "chroma_db"
OLLAMA_URL         = "http://localhost:11434"
EMBED_MODEL        = "nomic-embed-text"
COLLECTION_NAME    = "corpus"

# ── Helpers ───────────────────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TAG_RE         = re.compile(r"<[^>]+>")


def parse_md(path: Path) -> dict | None:
    """Return {id, title, doc_type, doc_group, text, path} or None on failure."""
    raw = path.read_text(encoding="utf-8", errors="replace")

    meta = {}
    m = FRONTMATTER_RE.match(raw)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"').strip("'")
        body = raw[m.end():]
    else:
        body = raw

    # Try to pull the numeric ID from the filename (e.g. 001_..., or infer later)
    stem = path.stem  # e.g. "01_amendment_i" or "declaration_of_independence"
    num_match = re.match(r"^(\d+)", stem)
    file_id = int(num_match.group(1)) if num_match else None

    title     = meta.get("title", path.stem.replace("_", " ").title())
    doc_type  = meta.get("doc_type",  "unknown")
    doc_group = path.parent.name  # directory name as group

    # Clean body text: strip markdown headers/bullets, collapse whitespace
    text = TAG_RE.sub("", body)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [text](url) → text
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return None

    return {
        "file_id":  file_id,
        "title":    title,
        "doc_type": doc_type,
        "group":    doc_group,
        "text":     text,
        "path":     str(path),
    }


def embed(texts: list[str]) -> list[list[float]]:
    """Call Ollama /api/embed and return list of embedding vectors."""
    resp = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": texts},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    # Ollama returns {"embeddings": [[...]]} or {"embedding": [...]} depending on version
    if "embeddings" in data:
        return data["embeddings"]
    if "embedding" in data:
        return [data["embedding"]]
    raise ValueError(f"Unexpected Ollama embed response keys: {list(data.keys())}")


def embed_one(text: str) -> list[float]:
    return embed([text])[0]


# ── Build ID → corpus doc mapping from submit.html ───────────────────────────

def load_corpus_index(html_path: Path) -> dict[int, dict]:
    """Parse the CORPUS JSON from submit.html to get authoritative ID→metadata."""
    html = html_path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"const CORPUS\s*=\s*(\[.*?\]);", html, re.DOTALL)
    if not m:
        return {}
    docs = json.loads(m.group(1))
    return {d["id"]: d for d in docs}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir", default=str(DEFAULT_CORPUS_DIR))
    ap.add_argument("--db-dir",     default=str(DEFAULT_DB_DIR))
    ap.add_argument("--reset",      action="store_true", help="delete & rebuild collection")
    args = ap.parse_args()

    corpus_dir = Path(args.corpus_dir)
    db_dir     = Path(args.db_dir)

    if not corpus_dir.exists():
        sys.exit(f"Corpus dir not found: {corpus_dir}")

    # Verify Ollama is running
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=5).raise_for_status()
    except Exception as e:
        sys.exit(f"Ollama not reachable at {OLLAMA_URL}: {e}\n"
                 f"Run: ollama serve   (and: ollama pull {EMBED_MODEL})")

    # Load authoritative CORPUS index from submit.html
    html_path = Path(__file__).parent / "submit.html"
    corpus_index = load_corpus_index(html_path) if html_path.exists() else {}
    print(f"Loaded {len(corpus_index)} docs from submit.html CORPUS index")

    # Collect markdown files
    md_files = sorted(corpus_dir.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files in {corpus_dir}")

    docs = []
    for path in md_files:
        parsed = parse_md(path)
        if not parsed:
            print(f"  SKIP (empty): {path.name}")
            continue
        docs.append(parsed)

    print(f"Parsed {len(docs)} valid docs")

    # Set up ChromaDB
    db_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_dir))

    if args.reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print("Deleted existing collection")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    existing = set(collection.get()["ids"])
    print(f"Existing docs in collection: {len(existing)}")

    # Embed and upsert in batches
    BATCH = 8
    added = skipped = 0

    for i in range(0, len(docs), BATCH):
        batch = docs[i : i + BATCH]

        # Build chroma IDs and check what needs updating
        to_add = []
        for doc in batch:
            # Prefer ID from submit.html CORPUS index (match by title)
            corpus_id = None
            for cid, cdata in corpus_index.items():
                if cdata["title"].lower() == doc["title"].lower():
                    corpus_id = cid
                    break
            chroma_id = f"doc_{corpus_id}" if corpus_id else f"file_{doc['path']}"

            doc["corpus_id"] = corpus_id
            doc["chroma_id"] = chroma_id

            if chroma_id in existing:
                skipped += 1
            else:
                to_add.append(doc)

        if not to_add:
            continue

        texts = [d["text"][:2000] for d in to_add]  # cap at 2k chars for embedding
        print(f"  Embedding {len(to_add)} docs (batch {i//BATCH + 1})…", end=" ", flush=True)

        try:
            vectors = embed(texts)
        except Exception as e:
            print(f"\n  ERROR embedding: {e}")
            continue

        collection.upsert(
            ids=[d["chroma_id"] for d in to_add],
            embeddings=vectors,
            documents=[d["text"][:2000] for d in to_add],
            metadatas=[{
                "corpus_id": d["corpus_id"] or -1,
                "title":     d["title"],
                "doc_type":  d["doc_type"],
                "group":     d["group"],
                "path":      d["path"],
            } for d in to_add],
        )
        added += len(to_add)
        print(f"✓ ({added} added so far)")

    print(f"\nDone. Added {added}, skipped {skipped} (already embedded).")
    print(f"Collection now has {collection.count()} docs.")
    print(f"\nDB at: {db_dir.resolve()}")
    print("Next: python3 ai_server.py")


if __name__ == "__main__":
    main()
