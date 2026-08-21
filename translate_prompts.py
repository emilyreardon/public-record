#!/usr/bin/env python3
"""
translate_prompts.py
====================
Translates the `prompt` field for all 137 corpus documents into Spanish,
writing results to `prompt_es` in submit.html.

Uses Ollama (must be running locally with olmo3-instruct).

Usage:
    python3 translate_prompts.py [--dry-run] [--ids 1,2,5]

Skips documents where `prompt_es` is already populated. Use --force to retranslate all.
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

SYSTEM_PROMPT = """You are a precise translator from English to Spanish.
Translate the given text into clear, plain Spanish at a 6th grade reading level.
Preserve the meaning exactly. Do not add or remove ideas.
Return ONLY the translated text, nothing else."""


def llm_translate(text: str) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model":   LLM_MODEL,
            "prompt":  f"Translate to Spanish:\n\n{text}",
            "system":  SYSTEM_PROMPT,
            "stream":  False,
            "options": {"num_predict": 300, "temperature": 0.2},
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip().strip('"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force",   action="store_true", help="Retranslate even if prompt_es exists")
    ap.add_argument("--ids",     help="Comma-separated doc IDs to process")
    args = ap.parse_args()

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

        prompt_en = doc.get("prompt", "").strip()
        if not prompt_en:
            print(f"  [{doc_id:3}] SKIP (no prompt): {doc['title'][:50]}")
            continue

        if not args.force and doc.get("prompt_es", "").strip():
            print(f"  [{doc_id:3}] OK   : {doc['title'][:50]}")
            continue

        print(f"  [{doc_id:3}] TRANSLATE: {doc['title'][:50]}")
        try:
            translation = llm_translate(prompt_en)
            print(f"         => {translation[:100]}")
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        if not args.dry_run:
            doc["prompt_es"] = translation

        updated += 1
        time.sleep(0.3)

    if args.dry_run:
        print(f"\nDry run: would have translated {updated} prompts.")
        return

    new_corpus  = json.dumps(corpus, ensure_ascii=False, separators=(",", ":"))
    new_content = content[:m.start(2)] + new_corpus + content[m.end(2):]
    HTML_PATH.write_text(new_content)
    print(f"\nDone. Translated {updated} prompt fields into Spanish.")
    print("Review, then: git add submit.html && git commit -m 'Translate prompt fields to Spanish' && git push origin main")


if __name__ == "__main__":
    main()
