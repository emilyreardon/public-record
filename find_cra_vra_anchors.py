import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")

FILES = {
    "civil_rights_act_1964_extracted.txt": ["Transcript", "Be it enacted", "The U.S. National Archives and Records Administration"],
    "voting_rights_act_1965_extracted.txt": ["Transcript", "Be it enacted", "The U.S. National Archives and Records Administration"],
}

for fname, anchors in FILES.items():
    path = os.path.join(BASE, fname)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    print("=" * 60)
    print(fname + "  total_len=" + str(len(text)))
    print("=" * 60)
    for anchor in anchors:
        count = text.count(anchor)
        idx = text.find(anchor)
        snippet = text[max(0,idx-40):idx+len(anchor)+60].replace(chr(10), " | ") if idx != -1 else ""
        print("  " + anchor + ": count=" + str(count) + " first_idx=" + str(idx))
        if idx != -1:
            print("    context: ..." + snippet + "...")
    print("")
    print("--- LAST 500 CHARS (to see footer shape) ---")
    print(text[-500:])
    print("")
