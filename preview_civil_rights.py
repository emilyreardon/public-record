import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")

FILES = [
    "civil_rights_act_1964_extracted.txt",
    "voting_rights_act_1965_extracted.txt",
]

for fname in FILES:
    path = os.path.join(BASE, fname)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    print("=" * 60)
    print(fname + "  total_len=" + str(len(text)))
    print("=" * 60)
    # Look for section/title markers that would indicate actual statutory text
    for marker in ["TITLE I", "Title I", "Section 1", "SEC. 1", "SEC. 2", "Be it enacted", "AN ACT"]:
        idx = text.find(marker)
        print("  " + marker + ": " + (str(idx) if idx != -1 else "NOT FOUND"))
    print("")
    print("--- chars 1500-3500 (past nav, where real content usually starts) ---")
    print(text[1500:3500])
    print("")
