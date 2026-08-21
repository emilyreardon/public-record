import os

RAW_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_core")

CHECKS = {
    "declaration_extracted.txt": [
        "IN CONGRESS", "unanimous Declaration", "July 4, 1776",
        "self-evident", "New Hampshire", "Georgia",
        "Explore the Documents", "Learn Their Story", "Online Exhibits",
    ],
    "constitution_extracted.txt": [
        "We the People", "Article I", "Article. I", "Article VII", "Article. VII",
        "Done in Convention", "Washington", "Explore the Documents",
        "Learn Their Story", "Online Exhibits",
    ],
    "amendments_1-10_extracted.txt": [
        "Amendment I", "Amendment X", "Congress shall make no law",
        "Explore the Documents", "Learn Their Story", "Online Exhibits",
    ],
    "amendments_11-27_extracted.txt": [
        "Amendment XI", "Amendment XXVII", "Amendment 27",
        "Explore the Documents", "Learn Their Story", "Online Exhibits",
    ],
}

for fname, anchors in CHECKS.items():
    path = os.path.join(RAW_DIR, fname)
    if not os.path.exists(path):
        print("MISSING: " + fname)
        continue
    with open(path, encoding="utf-8") as f:
        text = f.read()
    print("=" * 60)
    print(fname + "  total_len=" + str(len(text)))
    print("=" * 60)
    for anchor in anchors:
        idx = text.find(anchor)
        if idx == -1:
            print("  NOT FOUND: " + repr(anchor))
        else:
            print("  FOUND at index " + str(idx) + ": " + repr(anchor))
    print("")
