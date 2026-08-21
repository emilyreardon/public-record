import os, re

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
FEDREG_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "expansive", "federal_register")
os.makedirs(FEDREG_DIR, exist_ok=True)

def write_doc(filename, title, date, citation, source_url, body, tags):
    header = "---\n"
    header += "title: " + title + "\n"
    header += "tier: expansive\n"
    header += "doc_type: federal_register\n"
    header += "date: " + date + "\n"
    header += "citation: " + citation + "\n"
    header += "source_url: " + source_url + "\n"
    header += "source_name: National Archives and Records Administration, Milestone Documents\n"
    header += "source_type: primary_legal\n"
    header += "provenance_note: \n"
    header += "retrieval_tags: [" + tags + "]\n"
    header += "paired_with: []\n"
    header += "mobile_piece: \n"
    header += "verified: false\n"
    header += "---\n\n"
    visible_source = "Source: National Archives and Records Administration, Milestone Documents (" + source_url + ")\n\n"
    out_path = os.path.join(FEDREG_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + visible_source + body.strip() + "\n")
    print("wrote " + filename + " (" + str(len(body)) + " chars body)")
    print("--- first 300 chars of body ---")
    print(body.strip()[:300])
    print("")

# --- Civil Rights Act of 1964 ---
with open(os.path.join(BASE, "civil_rights_act_1964_extracted.txt"), encoding="utf-8") as f:
    text = f.read()
title_idx = text.find("An Act", 2000)
enacted_idx = text.find("Be it enacted")
start = title_idx if (title_idx != -1 and title_idx < enacted_idx) else enacted_idx
end = text.find("The U.S. National Archives and Records Administration")
body = text[start:end]
write_doc(
    "civil_rights_act_1964.md",
    "Civil Rights Act of 1964",
    "1964-07-02",
    "Civil Rights Act of 1964, Public Law 88-352, 78 Stat. 241",
    "https://www.archives.gov/milestone-documents/civil-rights-act",
    body,
    "civil rights act, 1964, discrimination, public accommodations, title vii"
)

# --- Voting Rights Act of 1965 ---
with open(os.path.join(BASE, "voting_rights_act_1965_extracted.txt"), encoding="utf-8") as f:
    text = f.read()
title_idx = text.find("An Act", 2000)
enacted_idx = text.find("Be it enacted")
start = title_idx if (title_idx != -1 and title_idx < enacted_idx) else enacted_idx
end = text.find("The U.S. National Archives and Records Administration")
body = text[start:end]
write_doc(
    "voting_rights_act_1965.md",
    "Voting Rights Act of 1965",
    "1965-08-06",
    "Voting Rights Act of 1965, Public Law 89-110, 79 Stat. 437",
    "https://www.archives.gov/milestone-documents/voting-rights-act",
    body,
    "voting rights act, 1965, fifteenth amendment, literacy tests, preclearance"
)

print("=== done ===")
