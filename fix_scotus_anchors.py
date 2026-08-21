import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
SCOTUS_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "expansive", "scotus")
os.makedirs(SCOTUS_DIR, exist_ok=True)

def write_doc(filename, title, citation, source_url, body):
    header = "---\n"
    header += "title: " + title + "\n"
    header += "tier: expansive\n"
    header += "doc_type: scotus_opinion\n"
    header += "citation: " + citation + "\n"
    header += "source_url: " + source_url + "\n"
    header += "source_name: Cornell Law School, Legal Information Institute\n"
    header += "source_type: primary_legal\n"
    header += "provenance_note: \n"
    header += "retrieval_tags: [scotus, repudiated decision]\n"
    header += "paired_with: []\n"
    header += "mobile_piece: \n"
    header += "verified: false\n"
    header += "---\n\n"
    visible_source = "Source: Cornell Law School, Legal Information Institute (" + source_url + ")\n\n"
    out_path = os.path.join(SCOTUS_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + visible_source + body.strip() + "\n")
    print("wrote " + filename + " (" + str(len(body)) + " chars body)")
    print("--- first 400 chars of body ---")
    print(body.strip()[:400])
    print("")

# --- Plessy ---
with open(os.path.join(BASE, "plessy_v_ferguson_extracted.txt"), encoding="utf-8") as f:
    text = f.read()
opinion_idx = text.find("delivered the opinion of the court")
case_name = "PLESSY v. FERGUSON."
start = text.rfind(case_name, 0, opinion_idx)
end = text.find("CC\u2205")
body = text[start:end]
write_doc(
    "plessy_v_ferguson.md",
    "Plessy v. Ferguson",
    "Plessy v. Ferguson, 163 U.S. 537 (1896)",
    "https://www.law.cornell.edu/supremecourt/text/163/537",
    body
)

# --- Korematsu ---
with open(os.path.join(BASE, "korematsu_extracted.txt"), encoding="utf-8") as f:
    text = f.read()
opinion_idx = text.find("delivered the opinion of the Court")
case_name = "TOYOSABURO KOREMATSU v. UNITED STATES."
start = text.rfind(case_name, 0, opinion_idx)
end = text.find("CC\u2205")
body = text[start:end]
write_doc(
    "korematsu_v_united_states.md",
    "Korematsu v. United States",
    "Korematsu v. United States, 323 U.S. 214 (1944)",
    "https://www.law.cornell.edu/supremecourt/text/323/214",
    body
)
