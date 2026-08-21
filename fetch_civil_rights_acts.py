import os, sys, time, re, html, requests

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
LOG_PATH = os.path.join(os.getcwd(), "new-public-systems-corpus", "_fetch_log.txt")
TIMEOUT = 20
MAX_RETRIES = 3
BACKOFF = 3

PAGES = [
    ("https://www.archives.gov/milestone-documents/civil-rights-act", "civil_rights_act_1964_raw.html"),
    ("https://www.archives.gov/milestone-documents/voting-rights-act", "voting_rights_act_1965_raw.html"),
]

def log(msg):
    print(msg)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    open(LOG_PATH, "a", encoding="utf-8").write(msg + "\n")

def clean(raw):
    t = re.sub("<script.*?</script>", "", raw, flags=re.S)
    t = re.sub("<style.*?</style>", "", t, flags=re.S)
    t = re.sub("<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub("[ \t]+", " ", t)
    t = re.sub("\n\\s*\n+", "\n\n", t)
    return t.strip()

def fetch_one(url, filename):
    out_path = os.path.join(BASE, filename)
    txt_path = out_path.replace("_raw.html", "_extracted.txt")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log("SKIP (already have): " + filename)
        return True
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log("Fetching " + url + " (attempt " + str(attempt) + ")...")
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            os.makedirs(BASE, exist_ok=True)
            open(out_path, "w", encoding="utf-8").write(r.text)
            open(txt_path, "w", encoding="utf-8").write(clean(r.text))
            log("OK: saved " + filename + " (" + str(len(r.text)) + " bytes)")
            return True
        except Exception as e:
            log("  attempt " + str(attempt) + " failed: " + repr(e))
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF * attempt)
    log("FAILED after retries: " + url)
    return False

def main():
    log("=== fetching civil rights acts into " + BASE + " ===")
    results = []
    for url, filename in PAGES:
        ok = fetch_one(url, filename)
        results.append((filename, ok))
        time.sleep(1)
    log("=== summary ===")
    for filename, ok in results:
        log(("OK  " if ok else "FAIL") + "  " + filename)
    log("done")

main()
