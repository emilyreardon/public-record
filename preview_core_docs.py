import os, re

RAW_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_core")

FILES = [
    "declaration_extracted.txt",
    "constitution_extracted.txt",
    "amendments_1-10_extracted.txt",
    "amendments_11-27_extracted.txt",
]

for fname in FILES:
    path = os.path.join(RAW_DIR, fname)
    if not os.path.exists(path):
        print("MISSING: " + fname)
        continue
    with open(path, encoding="utf-8") as f:
        text = f.read()
    print("=" * 60)
    print(fname + "  (" + str(len(text)) + " chars, " + str(len(text.split(chr(10)))) + " lines)")
    print("=" * 60)
    print("--- FIRST 600 CHARS ---")
    print(text[:600])
    print("--- LAST 600 CHARS ---")
    print(text[-600:])
    print("")
