import os
from pypdf import PdfReader

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
pdf_path = os.path.join(BASE, "treaty_new_echota_1835_raw.pdf")

reader = PdfReader(pdf_path)
print("Total pages: " + str(len(reader.pages)))

full_text = ""
for i, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    full_text += "\n\n=== PAGE " + str(i+1) + " ===\n\n" + text

out_path = os.path.join(BASE, "treaty_new_echota_1835_extracted.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print("Extracted " + str(len(full_text)) + " chars to treaty_new_echota_1835_extracted.txt")
print("")
print("--- FIRST 1000 CHARS ---")
print(full_text[:1000])
print("")
print("--- LAST 1000 CHARS ---")
print(full_text[-1000:])
