import os, re, html, requests

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
FEDREG_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "expansive", "federal_register")
os.makedirs(BASE, exist_ok=True)
os.makedirs(FEDREG_DIR, exist_ok=True)

url = "https://www.justice.gov/node/117521"

print("Fetching " + url + "...")
r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
r.raise_for_status()

raw_path = os.path.join(BASE, "title_ix_1975_regs_raw.html")
with open(raw_path, "w", encoding="utf-8") as f:
    f.write(r.text)
print("saved raw HTML (" + str(len(r.text)) + " bytes)")

def clean(raw):
    t = re.sub("<script.*?</script>", "", raw, flags=re.S)
    t = re.sub("<style.*?</style>", "", t, flags=re.S)
    t = re.sub("<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub("[ \t]+", " ", t)
    t = re.sub("\n\\s*\n+", "\n\n", t)
    return t.strip()

text = clean(r.text)
txt_path = os.path.join(BASE, "title_ix_1975_regs_extracted.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(text)
print("saved extracted text (" + str(len(text)) + " chars)")

start = text.find("Sec. 106.1 Purpose and effective date.")
end = text.find("U.S. Department of Justice\n950 Pennsylvania Avenue NW")
if end == -1:
    end = text.find("950 Pennsylvania Avenue NW")
body = text[start:end].strip()

print("body extracted: " + str(len(body)) + " chars, from index " + str(start) + " to " + str(end))
print("--- first 300 chars ---")
print(body[:300])
print("--- last 300 chars ---")
print(body[-300:])

header = "---\n"
header += "title: Title IX Implementing Regulations, 34 C.F.R. Part 106\n"
header += "tier: expansive\n"
header += "doc_type: federal_register\n"
header += "date: 1975-07-21\n"
header += "citation: 34 C.F.R. Part 106, Nondiscrimination on the Basis of Sex in Education Programs and Activities Receiving or Benefiting from Federal Financial Assistance (originally promulgated as 45 CFR Part 86, 40 FR 24128, June 4, 1975, effective July 21, 1975; recodified without substantive change as 34 CFR Part 106, 45 FR 30955, May 9, 1980)\n"
header += "source_url: https://www.justice.gov/node/117521\n"
header += "source_name: U.S. Department of Justice, Civil Rights Division, Federal Coordination and Compliance Section\n"
header += "source_type: primary_legal\n"
header += "provenance_note: This is the regulation as recodified into 34 CFR Part 106 in 1980 and archived by DOJ in this structure; it predates the substantial 2020 and 2024 rewrites of the grievance-procedure provisions and reflects the regulation's original 1975 structure and substance.\n"
header += "retrieval_tags: [title ix, education amendments, sex discrimination, athletics, 1975, federal regulation]\n"
header += "paired_with: []\n"
header += "mobile_piece: \n"
header += "verified: false\n"
header += "---\n\n"

visible_source = "Source: U.S. Department of Justice, Civil Rights Division (https://www.justice.gov/node/117521)\n"
visible_source += "Note: Archived pre-2020 text of 34 CFR Part 106, reflecting the regulation's original 1975 structure and substance before the 2020 and 2024 rewrites of its grievance-procedure provisions.\n\n"

out_path = os.path.join(FEDREG_DIR, "title_ix_1975_regulations.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(header + visible_source + body + "\n")

print("")
print("wrote title_ix_1975_regulations.md")
