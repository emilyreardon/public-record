import os, json, time, requests

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
meta_path = os.path.join(BASE, "douglass_loc_item_metadata.json")

with open(meta_path, encoding="utf-8") as f:
    data = json.load(f)

pages = data["resources"][0]["files"]
HEADERS = {"User-Agent": "Mozilla/5.0"}

for page_idx, page_files in enumerate(pages):
    for entry in page_files:
        if entry.get("mimetype") == "text/plain":
            url = entry["fulltext_service"]
            out_path = os.path.join(BASE, "douglass_loc_page" + str(page_idx + 1) + "_fulltext_raw.json")
            for attempt in range(1, 4):
                try:
                    print("Fetching page " + str(page_idx + 1) + " (attempt " + str(attempt) + ")...")
                    r = requests.get(url, headers=HEADERS, timeout=30)
                    r.raise_for_status()
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(r.text)
                    print("  OK: saved (" + str(len(r.text)) + " chars), content-type=" + r.headers.get("content-type", "?"))
                    print("  first 500 chars: " + r.text[:500].replace(chr(10), " | "))
                    break
                except Exception as e:
                    print("  attempt " + str(attempt) + " failed: " + repr(e))
                    if attempt < 3:
                        time.sleep(3)
            time.sleep(1)
