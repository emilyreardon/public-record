import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
path = os.path.join(BASE, "douglass_fourth_of_july_extracted.txt")

with open(path, encoding="utf-8") as f:
    text = f.read()

print("=== all 'Document' occurrences with context ===")
start_search = 0
while True:
    idx = text.find("Document", start_search)
    if idx == -1:
        break
    snippet = text[idx:idx+300].replace(chr(10), " | ")
    print(str(idx) + ": " + snippet)
    print("---")
    start_search = idx + 1
