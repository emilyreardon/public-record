import os, re

RAW_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_core")
DECL_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "core", "declaration")
CONST_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "core", "constitution")
AMEND_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "core", "amendments")

for d in [DECL_DIR, CONST_DIR, AMEND_DIR]:
    os.makedirs(d, exist_ok=True)

def load(fname):
    path = os.path.join(RAW_DIR, fname)
    with open(path, encoding="utf-8") as f:
        return f.read()

def header(title, doc_type, date, citation, source_url, tags):
    h = "---\n"
    h += "title: " + title + "\n"
    h += "tier: core\n"
    h += "doc_type: " + doc_type + "\n"
    h += "date: " + date + "\n"
    h += "citation: " + citation + "\n"
    h += "source_url: " + source_url + "\n"
    h += "source_name: National Archives\n"
    h += "retrieval_tags: [" + tags + "]\n"
    h += "paired_with: []\n"
    h += "mobile_piece: resin_tablet\n"
    h += "verified: false\n"
    h += "---\n\n"
    return h

written = []

# --- Declaration ---
text = load("declaration_extracted.txt")
start = text.find("In Congress")
end = text.rfind("Online Exhibits")
body = text[start:end].strip()
out = header(
    "Declaration of Independence", "declaration", "1776-07-04",
    "In Congress, July 4, 1776. The unanimous Declaration of the thirteen united States of America.",
    "https://www.archives.gov/founding-docs/declaration-transcript",
    "founding, independence, grievances, natural rights, consent of the governed, self-evident, tyranny"
) + body + "\n"
out_path = os.path.join(DECL_DIR, "declaration_of_independence.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(out)
written.append(out_path)
print("wrote declaration_of_independence.md (" + str(len(body)) + " chars body)")

# --- Constitution ---
text = load("constitution_extracted.txt")
start = text.find("We the People")
end = text.rfind("Online Exhibits")
body = text[start:end].strip()
out = header(
    "Constitution of the United States, Articles I-VII", "constitution", "1787-09-17",
    "U.S. Const. arts. I-VII",
    "https://www.archives.gov/founding-docs/constitution-transcript",
    "constitution, articles, legislative, executive, judicial, federalism, amendment process, ratification"
) + body + "\n"
out_path = os.path.join(CONST_DIR, "constitution_articles.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(out)
written.append(out_path)
print("wrote constitution_articles.md (" + str(len(body)) + " chars body)")

# --- Amendments 1-10 ---
text = load("amendments_1-10_extracted.txt")
preamble_start = text.find("Congress of the United States begun and held")
end = text.rfind("Online Exhibits")
full_block = text[preamble_start:end].strip()

# Find each "Amendment <roman>" header (title-case, as seen in this file)
matches = list(re.finditer(r"Amendment ([IVXL]+)\b", full_block))
ROMAN_TO_INT = {"I":1,"II":2,"III":3,"IV":4,"V":5,"VI":6,"VII":7,"VIII":8,"IX":9,"X":10}
ROMAN_NAMES = {1:"i",2:"ii",3:"iii",4:"iv",5:"v",6:"vi",7:"vii",8:"viii",9:"ix",10:"x"}

seen = {}
for m in matches:
    roman = m.group(1)
    num = ROMAN_TO_INT.get(roman)
    if num and num not in seen:
        seen[num] = m.start()

nums_sorted = sorted(seen.keys())
for i, num in enumerate(nums_sorted):
    s = seen[num]
    e = seen[nums_sorted[i+1]] if i+1 < len(nums_sorted) else len(full_block)
    chunk = full_block[s:e].strip()
    fname = str(num).zfill(2) + "_amendment_" + ROMAN_NAMES[num] + ".md"
    out = header(
        "Amendment " + ["","I","II","III","IV","V","VI","VII","VIII","IX","X"][num],
        "amendment", "1791-12-15",
        "U.S. Const. amend. " + ["","I","II","III","IV","V","VI","VII","VIII","IX","X"][num],
        "https://www.archives.gov/founding-docs/bill-of-rights-transcript",
        "bill of rights, amendment " + str(num)
    ) + chunk + "\n"
    out_path = os.path.join(AMEND_DIR, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    written.append(out_path)
    print("wrote " + fname + " (" + str(len(chunk)) + " chars body)")

# --- Amendments 11-27 ---
text = load("amendments_11-27_extracted.txt")
toc_cutoff = text.find("On This Page")
if toc_cutoff == -1:
    toc_cutoff = text.rfind("Online Exhibits")

matches = list(re.finditer(r"AMENDMENT ([IVXL]+)\b", text[:toc_cutoff]))
ROMAN_TO_INT2 = {
    "XI":11,"XII":12,"XIII":13,"XIV":14,"XV":15,"XVI":16,"XVII":17,"XVIII":18,
    "XIX":19,"XX":20,"XXI":21,"XXII":22,"XXIII":23,"XXIV":24,"XXV":25,"XXVI":26,"XXVII":27,
}
ROMAN_NAMES2 = {
    11:"xi",12:"xii",13:"xiii",14:"xiv",15:"xv",16:"xvi",17:"xvii",18:"xviii",
    19:"xix",20:"xx",21:"xxi",22:"xxii",23:"xxiii",24:"xxiv",25:"xxv",26:"xxvi",27:"xxvii",
}

seen2 = {}
for m in matches:
    roman = m.group(1)
    num = ROMAN_TO_INT2.get(roman)
    if num and num not in seen2:
        seen2[num] = m.start()

nums_sorted2 = sorted(seen2.keys())
for i, num in enumerate(nums_sorted2):
    s = seen2[num]
    e = seen2[nums_sorted2[i+1]] if i+1 < len(nums_sorted2) else toc_cutoff
    chunk = text[s:e].strip()
    roman = ROMAN_NAMES2[num].upper()
    fname = str(num).zfill(2) + "_amendment_" + ROMAN_NAMES2[num] + ".md"
    out = header(
        "Amendment " + roman,
        "amendment", "unknown",
        "U.S. Const. amend. " + roman,
        "https://www.archives.gov/founding-docs/amendments-11-27",
        "constitution, amendment " + str(num)
    ) + chunk + "\n"
    out_path = os.path.join(AMEND_DIR, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    written.append(out_path)
    print("wrote " + fname + " (" + str(len(chunk)) + " chars body)")

print("")
print("=== summary ===")
print("total files written: " + str(len(written)))
expected_amendments = set(range(1,28))
found_amendments = set(nums_sorted) | set(nums_sorted2)
missing = expected_amendments - found_amendments
print("amendments found: " + str(sorted(found_amendments)))
print("amendments MISSING: " + str(sorted(missing)))
