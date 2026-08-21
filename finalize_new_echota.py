import os, re

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
TREATY_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "expansive", "treaties")
os.makedirs(TREATY_DIR, exist_ok=True)

with open(os.path.join(BASE, "treaty_new_echota_1835_extracted.txt"), encoding="utf-8") as f:
    text = f.read()

# Strip the page-marker artifacts added during extraction (not part of the original document)
body = re.sub(r"\n\n=== PAGE \d+ ===\n\n", "\n\n", text).strip()

header = "---\n"
header += "title: Treaty of New Echota\n"
header += "tier: expansive\n"
header += "doc_type: treaty\n"
header += "date: 1835-12-29\n"
header += "citation: Treaty with the Cherokee, 1835 (7 Stat. 478), concluded at New Echota, Georgia, December 29, 1835; ratified May 23, 1836\n"
header += "source_url: https://www.govinfo.gov/content/pkg/STATUTE-7/pdf/STATUTE-7-Pg478.pdf\n"
header += "source_name: U.S. Statutes at Large, Volume 7 (U.S. Government Publishing Office, govinfo.gov)\n"
header += "source_type: primary_legal\n"
header += "provenance_note: Signed by a minority Treaty Party faction without authorization from the Cherokee National Council or Principal Chief John Ross; ratified by the U.S. Senate by a single vote in 1836. It provided the legal basis for the forced removal of the Cherokee Nation known as the Trail of Tears.\n"
header += "retrieval_tags: [new echota, cherokee, trail of tears, indian removal, treaty]\n"
header += "paired_with: []\n"
header += "mobile_piece: \n"
header += "verified: false\n"
header += "---\n\n"

visible_source = "Source: U.S. Statutes at Large, Volume 7 (U.S. Government Publishing Office, govinfo.gov) (https://www.govinfo.gov/content/pkg/STATUTE-7/pdf/STATUTE-7-Pg478.pdf)\n"
visible_source += "Note: Signed by a minority Treaty Party faction without authorization from the Cherokee National Council or Principal Chief John Ross; ratified by the U.S. Senate by a single vote in 1836. It provided the legal basis for the forced removal of the Cherokee Nation known as the Trail of Tears.\n\n"

out_path = os.path.join(TREATY_DIR, "treaty_new_echota_1835.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(header + visible_source + body + "\n")

print("wrote treaty_new_echota_1835.md (" + str(len(body)) + " chars body)")
