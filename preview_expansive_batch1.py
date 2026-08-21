import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")

FILES = [
    "declaration_of_sentiments_extracted.txt",
    "douglass_fourth_of_july_extracted.txt",
    "sojourner_truth_extracted.txt",
    "chief_joseph_surrender_extracted.txt",
    "fort_laramie_treaty_1868_extracted.txt",
    "dred_scott_extracted.txt",
    "plessy_v_ferguson_extracted.txt",
    "korematsu_extracted.txt",
    "eo_9066_extracted.txt",
    "eo_8802_extracted.txt",
]

for fname in FILES:
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print("MISSING: " + fname)
        continue
    with open(path, encoding="utf-8") as f:
        text = f.read()
    print("=" * 60)
    print(fname + "  total_len=" + str(len(text)))
    print("=" * 60)
    print("--- FIRST 500 ---")
    print(text[:500])
    print("--- LAST 500 ---")
    print(text[-500:])
    print("")
