import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")

CHECKS = {
    "declaration_of_sentiments_extracted.txt": [
        "When, in the course of human events",
        "When in the course of human events",
        "Park footer",
        "Last updated",
    ],
    "douglass_fourth_of_july_extracted.txt": [
        "Fellow-citizens, pardon me",
        "Statement of Principles",
    ],
    "sojourner_truth_extracted.txt": [
        "I want to say a few words",
        "Statement of Principles",
    ],
    "chief_joseph_surrender_extracted.txt": [
        "Tell General Howard",
        "Statement of Principles",
    ],
    "fort_laramie_treaty_1868_extracted.txt": [
        "ARTICLES OF",
        "\u00a9 2008 Lillian Goldman",
    ],
    "dred_scott_extracted.txt": [
        "December Term, 1856",
        "THIS case was brought up",
        "CC\u2205",
    ],
    "plessy_v_ferguson_extracted.txt": [
        "delivered the opinion of the court",
        "October Term",
        "CC\u2205",
    ],
    "korematsu_extracted.txt": [
        "delivered the opinion of the Court",
        "October Term",
        "CC\u2205",
    ],
    "eo_9066_extracted.txt": [
        "Citation:",
        "Whereas the successful prosecution",
        "The U.S. National Archives and Records Administration",
    ],
    "eo_8802_extracted.txt": [
        "Citation:",
        "NOW, THEREFORE",
        "The U.S. National Archives and Records Administration",
    ],
}

for fname, anchors in CHECKS.items():
    path = os.path.join(BASE, fname)
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
            snippet = text[max(0,idx-40):idx+len(anchor)+60].replace(chr(10), " | ")
            print("  FOUND at " + str(idx) + " (count=" + str(count) + "): " + repr(anchor))
            print("    context: ..." + snippet + "...")
    print("")
