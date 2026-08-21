import os

RAW_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_core")

FOOTER_ANCHOR = "The U.S. National Archives and Records Administration"

CHECKS = {
    "declaration_extracted.txt": [
        "When in the Course of human events",
        "IN CONGRESS", "In Congress",
        "New Hampshire", "Georgia",
        FOOTER_ANCHOR,
    ],
    "constitution_extracted.txt": [
        "We the People of the United States",
        "Done in Convention",
        "Article. VII", "Article VII",
        FOOTER_ANCHOR,
    ],
    "amendments_1-10_extracted.txt": [
        "Congress of the United States",
        "begun and held at the City of New-York",
        "Amendment I", "Amendment X",
        FOOTER_ANCHOR,
    ],
    "amendments_11-27_extracted.txt": [
        "Amendment 11", "Amendment XI", "Eleventh Amendment",
        "Amendment 27", "Amendment XXVII", "Twenty-seventh Amendment",
        "Amendment 12", "Amendment 13", "Amendment 14",
        FOOTER_ANCHOR,
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
            count = text.count(anchor)
            snippet = text[max(0,idx-40):idx+len(anchor)+40].replace(chr(10), " | ")
            print("  FOUND at " + str(idx) + " (count=" + str(count) + "): " + repr(anchor))
            print("    context: ..." + snippet + "...")
    print("")
