import os, time, requests

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
os.makedirs(BASE, exist_ok=True)

PAGES = [
    ("https://chroniclingamerica.loc.gov/lccn/sn84026366/1852-07-09/ed-1/seq-1/ocr.txt", "douglass_loc_seq1.txt"),
    ("https://chroniclingamerica.loc.gov/lccn/sn84026366/1852-07-09/ed-1/seq-2/ocr.txt", "douglass_loc_seq2.txt"),
    ("https://chroniclingamerica.loc.gov/lccn/sn84026366/1852-07-09/ed-1/seq-3/ocr.txt", "douglass_loc_seq3.txt"),
    ("https://chroniclingamerica.loc.gov/lccn/sn84026366/1852-07-09/ed-1/seq-4/ocr.txt", "douglass_loc_seq4.txt"),
]

for url, filename in PAGES:
    out_path = os.path.join(BASE, filename)
    for attempt in range(1, 4):
        try:
            print("Fetching " + url + " (attempt " + str(attempt) + ")...")
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(r.text)
            print("OK: saved " + filename + " (" + str(len(r.text)) + " chars)")
            break
        except Exception as e:
            print("  attempt " + str(attempt) + " failed: " + repr(e))
            if attempt < 3:
                time.sleep(3 * attempt)
    time.sleep(1)

print("")
print("=== previewing for 'Corinthian Hall' occurrences across pages ===")
for url, filename in PAGES:
    out_path = os.path.join(BASE, filename)
    if not os.path.exists(out_path):
        continue
    with open(out_path, encoding="utf-8") as f:
        text = f.read()
    idx = text.find("Corinthian")
    print(filename + ": len=" + str(len(text)) + " 'Corinthian' first found at " + str(idx))
    if idx != -1:
        print("  context: " + text[max(0,idx-100):idx+300].replace(chr(10), " | "))
