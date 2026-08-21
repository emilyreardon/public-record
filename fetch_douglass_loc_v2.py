import os, time, json, requests
BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
os.makedirs(BASE, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
}
item_url = "https://www.loc.gov/item/sn84026366/1852-07-09/ed-1/?fo=json"
print("Fetching item metadata: " + item_url)
r = requests.get(item_url, headers=HEADERS, timeout=20)
r.raise_for_status()
data = r.json()
meta_path = os.path.join(BASE, "douglass_loc_item_metadata.json")
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("saved metadata (" + str(len(r.text)) + " chars)")
resources = data.get("resources", [])
print("found " + str(len(resources)) + " resource entries")
for i, res in enumerate(resources):
    print("--- resource " + str(i) + " keys: " + str(list(res.keys())))
    for key in ["fulltext_file", "fulltext_derivative", "text"]:
        if key in res:
            print("  " + key + ": " + str(res[key]))
pages = data.get("segments", data.get("resources", []))
print("")
print("=== attempting to locate per-page fulltext links ===")
# The item JSON usually has a top-level 'item' with 'resources' containing per-page image/text links
if "resources" in data:
    for i, res in enumerate(data["resources"]):
        pgtext = res.get("files")
        print("resource " + str(i) + " raw dump (first 2000 chars):")
        print(json.dumps(res, indent=2)[:2000])
