#!/usr/bin/env python3
"""
rewrite_prompts.py
==================
Rewrites the `do` / `do_en` instruction field for all 137 corpus documents
using Ollama (must be running locally).

Usage:
    python3 rewrite_prompts.py [--dry-run] [--ids 1,2,5]

Writes results back to submit.html. Make a git backup first.

Skips documents where `do_en` is already in good shape (short, plain, no dashes,
no mention of "representatives"). Use --force to rewrite all.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434"
LLM_MODEL  = "olmo3-instruct"
HTML_PATH  = Path(__file__).parent / "submit.html"

# Documents we've already carefully hand-crafted — skip unless --force
SKIP_IDS = {30, 76}  # Federalist No. 1, Federalist No. 47

SYSTEM_PROMPT = """You write short instructions for visitors at a civic art installation about American democracy.
Each instruction appears above a text box where the visitor will write their response.
The response will later be submitted — as written — to their elected representatives.

Your job: write 2-3 short sentences that follow this exact structure:
1. A simple question or observation that surfaces the key idea of the document in everyday terms.
   Use something a 10-year-old would recognize from their own life. No jargon.
2. Ask them to name a real example of a problem they see — something specific, from life, not abstract.
3. Ask them to write one idea for how to fix or change it.

Rules:
- No dashes of any kind
- No mention of "representatives", "Congress", "branches", or government institutions
- Maximum one new concept per instruction
- Plain language, 6th grade level
- A kid should care about this
- Do NOT start with "Think about" every time, vary the opening
- 2-3 sentences total, nothing more
- Return ONLY the instruction text, no labels, no explanation"""


def llm(prompt: str) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model":   LLM_MODEL,
            "prompt":  prompt,
            "system":  SYSTEM_PROMPT,
            "stream":  False,
            "options": {"num_predict": 120, "temperature": 0.5},
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip().strip('"')


def rewrite_one(doc: dict) -> str:
    title   = doc.get("title", "")
    desc    = doc.get("desc_en", "") or ""
    prompt  = doc.get("prompt", "") or ""

    user_prompt = (
        f"Document title: {title}\n"
        f"Summary: {desc[:300]}\n"
        f"Visitor prompt: {prompt[:200]}\n\n"
        "Write the instruction."
    )

    try:
        result = llm(user_prompt)
        # Strip any em dashes or regular dashes from result
        result = result.replace("—", ".").replace(" - ", ". ")
        return result
    except Exception as e:
        print(f"  ERROR on id={doc['id']}: {e}")
        return doc.get("do_en", "") or doc.get("do", "")


def already_good(do_text: str) -> bool:
    """Returns True if the instruction already looks well-formed."""
    if not do_text:
        return False
    if len(do_text) > 400:
        return False
    if "___" in do_text:
        return False
    if " — " in do_text or " - " in do_text:
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print output, don't write file")
    ap.add_argument("--force",   action="store_true", help="Rewrite all, including hand-crafted docs")
    ap.add_argument("--ids",     help="Comma-separated list of doc IDs to rewrite (default: all)")
    args = ap.parse_args()

    # Ping Ollama
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=5).raise_for_status()
    except Exception:
        print("Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    content = HTML_PATH.read_text()
    m = re.search(r"(const CORPUS\s*=\s*)(\[.*?\])(;)", content, re.DOTALL)
    if not m:
        print("Could not find CORPUS in submit.html")
        sys.exit(1)

    corpus = json.loads(m.group(2))

    target_ids = None
    if args.ids:
        target_ids = set(int(x) for x in args.ids.split(","))

    updated = 0
    for doc in corpus:
        doc_id = doc["id"]

        if target_ids and doc_id not in target_ids:
            continue

        if not args.force and doc_id in SKIP_IDS:
            print(f"  [{doc_id:3}] SKIP (hand-crafted): {doc['title'][:50]}")
            continue

        current_do = doc.get("do_en", "") or doc.get("do", "")

        if not args.force and already_good(current_do):
            print(f"  [{doc_id:3}] OK   : {doc['title'][:50]}")
            continue

        print(f"  [{doc_id:3}] REWRITE: {doc['title'][:50]}")
        new_do = rewrite_one(doc)
        print(f"         => {new_do[:100]}")

        if not args.dry_run:
            doc["do"]    = new_do
            doc["do_en"] = new_do

        updated += 1
        time.sleep(0.5)  # gentle on Ollama

    if args.dry_run:
        print(f"\nDry run: would have updated {updated} documents.")
        return

    new_corpus  = json.dumps(corpus, ensure_ascii=False, separators=(",", ":"))
    new_content = content[:m.start(2)] + new_corpus + content[m.end(2):]
    HTML_PATH.write_text(new_content)
    print(f"\nDone. Updated {updated} documents in submit.html.")
    print("Review the changes, then: git add submit.html && git commit -m 'AI-rewrite do_en prompts' && git push origin main")


if __name__ == "__main__":
    main()
