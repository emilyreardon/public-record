import os, json

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
meta_path = os.path.join(BASE, "douglass_loc_item_metadata.json")

with open(meta_path, encoding="utf-8") as f:
    data = json.load(f)

pages = data["resources"][0]["files"]
print("total pages in this issue: " + str(len(pages)))
print("")

for page_idx, page_files in enumerate(pages):
    print("=== page " + str(page_idx + 1) + " ===")
    for entry in page_files:
        mimetype = entry.get("mimetype", "?")
        url = entry.get("url", "?")
        print("  " + mimetype + ": " + url)
    print("")
