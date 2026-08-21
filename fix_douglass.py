import os

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
CORPUS = os.path.join(os.getcwd(), "new-public-systems-corpus", "expansive")
MOVEMENT_DIR = os.path.join(CORPUS, "movement_docs")
os.makedirs(MOVEMENT_DIR, exist_ok=True)

with open(os.path.join(BASE, "douglass_fourth_of_july_extracted.txt"), encoding="utf-8") as f:
    text = f.read()

start = text.find("My subject, then fellow-citizens, is American slavery")
end = text.find("Statement of Principles")
body = text[start:end].strip()

header = "---\n"
header += "title: What to the Slave is the Fourth of July?\n"
header += "tier: expansive\n"
header += "doc_type: movement_doc\n"
header += "date: 1852-07-05\n"
header += "citation: Frederick Douglass, address to the Rochester Ladies' Anti-Slavery Society, July 5, 1852\n"
header += "source_url: https://teachingamericanhistory.org/document/what-to-the-slave-is-the-fourth-of-july-3/\n"
header += "source_name: Teaching American History (Ashbrook Center, Ashland University)\n"
header += "source_type: educational_transcription\n"
header += "provenance_note: This version is abridged (opens mid-speech) rather than the complete oration; text drawn from Frederick Douglass: Selected Speeches and Writings, ed. Philip S. Foner (Chicago: Lawrence Hill, 1999), 188-206, via the University of Rochester's Frederick Douglass Project.\n"
header += "retrieval_tags: [douglass, fourth of july, abolition, hypocrisy, declaration of independence]\n"
header += "paired_with: []\n"
header += "mobile_piece: \n"
header += "verified: false\n"
header += "---\n\n"

visible_source = "Source: Teaching American History (https://teachingamericanhistory.org/document/what-to-the-slave-is-the-fourth-of-july-3/)\n"
visible_source += "Note: This version is abridged (opens mid-speech) rather than the complete oration; text drawn from Frederick Douglass: Selected Speeches and Writings, ed. Philip S. Foner (Chicago: Lawrence Hill, 1999), 188-206, via the University of Rochester's Frederick Douglass Project.\n\n"

out_path = os.path.join(MOVEMENT_DIR, "douglass_what_to_the_slave.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(header + visible_source + body + "\n")

print("wrote douglass_what_to_the_slave.md (" + str(len(body)) + " chars body)")
