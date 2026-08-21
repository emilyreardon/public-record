import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
CORPUS = os.path.join(os.getcwd(), "new-public-systems-corpus", "expansive")

DIRS = {
    "sentiments": os.path.join(CORPUS, "declaration_of_sentiments"),
    "movement": os.path.join(CORPUS, "movement_docs"),
    "treaties": os.path.join(CORPUS, "treaties"),
    "scotus": os.path.join(CORPUS, "scotus"),
    "fedreg": os.path.join(CORPUS, "federal_register"),
}
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

def load(fname):
    with open(os.path.join(BASE, fname), encoding="utf-8") as f:
        return f.read()

def write_doc(out_dir, filename, title, tier, doc_type, date, citation,
              source_url, source_name, source_type, provenance_note,
              retrieval_tags, body):
    header = "---\n"
    header += "title: " + title + "\n"
    header += "tier: " + tier + "\n"
    header += "doc_type: " + doc_type + "\n"
    header += "date: " + date + "\n"
    header += "citation: " + citation + "\n"
    header += "source_url: " + source_url + "\n"
    header += "source_name: " + source_name + "\n"
    header += "source_type: " + source_type + "\n"
    header += "provenance_note: " + provenance_note + "\n"
    header += "retrieval_tags: [" + retrieval_tags + "]\n"
    header += "paired_with: []\n"
    header += "mobile_piece: \n"
    header += "verified: false\n"
    header += "---\n\n"
    visible_source = "Source: " + source_name + " (" + source_url + ")\n"
    if provenance_note.strip():
        visible_source += "Note: " + provenance_note + "\n"
    visible_source += "\n"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + visible_source + body.strip() + "\n")
    print("wrote " + filename + " (" + str(len(body)) + " chars body)")

# --- Declaration of Sentiments ---
text = load("declaration_of_sentiments_extracted.txt")
body = text[992:8587].strip()
write_doc(
    DIRS["sentiments"], "declaration_of_sentiments.md",
    "Declaration of Sentiments", "expansive", "movement_doc", "1848-07-20",
    "Declaration of Sentiments, Seneca Falls Convention, July 19-20, 1848",
    "https://www.nps.gov/wori/learn/historyculture/declaration-of-sentiments.htm",
    "National Park Service, Women's Rights National Historical Park",
    "government_transcription",
    "The original 1848 manuscript has never been located; this NPS transcription derives from period reprints, not the lost original.",
    "sentiments, seneca falls, women's rights, suffrage, stanton",
    body
)

# --- Movement docs ---
text = load("douglass_fourth_of_july_extracted.txt")
start = text.find("The fact is, ladies and gentlemen, the distance between this platform")
end = text.find("Statement of Principles")
body = text[start:end].strip() if start != -1 and end != -1 else ""
if not body:
    print("WARNING: douglass anchors not found as expected, skipping - check manually")
else:
    write_doc(
        DIRS["movement"], "douglass_what_to_the_slave.md",
        "What to the Slave is the Fourth of July?", "expansive", "movement_doc", "1852-07-05",
        "Frederick Douglass, address to the Rochester Ladies' Anti-Slavery Society, July 5, 1852",
        "https://teachingamericanhistory.org/document/what-to-the-slave-is-the-fourth-of-july-3/",
        "Teaching American History (Ashbrook Center, Ashland University)",
        "educational_transcription",
        "Educational-archive transcription of the 1852 printed oration (Lee, Mann & Co.), not a government archival source.",
        "douglass, fourth of july, abolition, hypocrisy, declaration of independence",
        body
    )

text = load("sojourner_truth_extracted.txt")
start = text.find("I want to say a few words")
end = text.find("Statement of Principles")
body = text[start:end].strip()
write_doc(
    DIRS["movement"], "sojourner_truth_aint_i_a_woman.md",
    "Ain't I a Woman?", "expansive", "movement_doc", "1851-05-29",
    "Sojourner Truth, address to the Ohio Women's Rights Convention, Akron, May 29, 1851 (Marius Robinson transcription, Anti-Slavery Bugle, June 21, 1851)",
    "https://teachingamericanhistory.org/document/aint-i-a-woman/",
    "Teaching American History (Ashbrook Center, Ashland University)",
    "educational_transcription",
    "This is the Robinson 1851 version, now understood by historians to be more accurate than the widely circulated 1863 Frances Gage version, which added a fabricated Southern dialect Truth (a native New Yorker) did not have.",
    "sojourner truth, women's rights, abolition, akron convention",
    body
)

text = load("chief_joseph_surrender_extracted.txt")
start = text.find("Tell General Howard")
end = text.find("Statement of Principles")
body = text[start:end].strip()
write_doc(
    DIRS["movement"], "chief_joseph_surrender.md",
    "I Will Fight No More Forever", "expansive", "movement_doc", "1877-10-05",
    "Chief Joseph, surrender speech, Bear Paw Mountains, Montana Territory, October 5, 1877",
    "https://teachingamericanhistory.org/document/i-will-fight-no-more-forever/",
    "Teaching American History (Ashbrook Center, Ashland University)",
    "educational_transcription",
    "Chief Joseph spoke Nez Perce; this English text was recorded after the fact by Lieutenant C.E.S. Wood and printed in Harper's Weekly, Nov. 17, 1877. Some historians question how much of the phrasing is Wood's rather than Joseph's own words.",
    "chief joseph, nez perce, surrender, indian wars, 1877",
    body
)

# --- Treaty: Fort Laramie ---
text = load("fort_laramie_treaty_1868_extracted.txt")
body = text[488:29162].strip()
write_doc(
    DIRS["treaties"], "fort_laramie_treaty_1868.md",
    "Treaty of Fort Laramie", "expansive", "treaty", "1868-04-29",
    "Treaty with the Sioux-Brule, Oglala, Miniconjou, Yanktonai, Hunkpapa, Blackfeet, Cuthead, Two Kettle, Sans Arcs, and Santee, and Arapaho, April 29, 1868",
    "https://avalon.law.yale.edu/19th_century/nt001.asp",
    "Avalon Project, Lillian Goldman Law Library, Yale Law School",
    "primary_legal",
    "",
    "fort laramie, sioux, lakota, treaty, black hills, 1868",
    body
)

# --- SCOTUS opinions ---
text = load("dred_scott_extracted.txt")
body = text[1261:646875].strip()
write_doc(
    DIRS["scotus"], "dred_scott_v_sandford.md",
    "Dred Scott v. Sandford", "expansive", "scotus_opinion", "1857-03-06",
    "Dred Scott v. Sandford, 60 U.S. 393 (1857)",
    "https://www.law.cornell.edu/supremecourt/text/60/393",
    "Cornell Law School, Legal Information Institute",
    "primary_legal",
    "",
    "dred scott, slavery, citizenship, missouri compromise, repudiated decision",
    body
)

text = load("plessy_v_ferguson_extracted.txt")
plessy_anchor = text.find("delivered the opinion of the court")
start = max(0, plessy_anchor - 600)
end = text.find("CC\u2205")
body = text[start:end].strip()
write_doc(
    DIRS["scotus"], "plessy_v_ferguson.md",
    "Plessy v. Ferguson", "expansive", "scotus_opinion", "1896-05-18",
    "Plessy v. Ferguson, 163 U.S. 537 (1896)",
    "https://www.law.cornell.edu/supremecourt/text/163/537",
    "Cornell Law School, Legal Information Institute",
    "primary_legal",
    "Extraction used an approximate start point (600-char buffer before the opinion text) rather than a confirmed exact anchor; check the first few lines for stray site navigation before finalizing.",
    "plessy, segregation, separate but equal, repudiated decision",
    body
)

text = load("korematsu_extracted.txt")
korematsu_anchor = text.find("delivered the opinion of the Court")
start = max(0, korematsu_anchor - 600)
end = text.find("CC\u2205")
body = text[start:end].strip()
write_doc(
    DIRS["scotus"], "korematsu_v_united_states.md",
    "Korematsu v. United States", "expansive", "scotus_opinion", "1944-12-18",
    "Korematsu v. United States, 323 U.S. 214 (1944)",
    "https://www.law.cornell.edu/supremecourt/text/323/214",
    "Cornell Law School, Legal Information Institute",
    "primary_legal",
    "Extraction used an approximate start point (600-char buffer before the opinion text) rather than a confirmed exact anchor; check the first few lines for stray site navigation before finalizing.",
    "korematsu, japanese american incarceration, executive order 9066, repudiated decision",
    body
)

# --- Federal Register / Executive Orders ---
text = load("eo_9066_extracted.txt")
body = text[6817:11616].strip()
write_doc(
    DIRS["fedreg"], "executive_order_9066.md",
    "Executive Order 9066", "expansive", "federal_register", "1942-02-19",
    "Executive Order 9066, February 19, 1942",
    "https://www.archives.gov/milestone-documents/executive-order-9066",
    "National Archives and Records Administration, Milestone Documents",
    "primary_archival",
    "",
    "executive order 9066, japanese american incarceration, world war ii",
    body
)

text = load("eo_8802_extracted.txt")
body = text[4424:8064].strip()
write_doc(
    DIRS["fedreg"], "executive_order_8802.md",
    "Executive Order 8802", "expansive", "federal_register", "1941-06-25",
    "Executive Order 8802, June 25, 1941",
    "https://www.archives.gov/milestone-documents/executive-order-8802",
    "National Archives and Records Administration, Milestone Documents",
    "primary_archival",
    "",
    "executive order 8802, fair employment, discrimination, a philip randolph",
    body
)

print("")
print("=== done ===")
