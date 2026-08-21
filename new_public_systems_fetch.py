import os, sys, time, re, html, requests

OUT_DIR = os.path.join(os.getcwd(), "new-public-systems-corpus", "core", "federalist")
LOG_PATH = os.path.join(os.getcwd(), "new-public-systems-corpus", "_fetch_log.txt")
TIMEOUT = 20
MAX_RETRIES = 3
BACKOFF = 3

PAGES = [
    ("https://guides.loc.gov/federalist-papers/text-1-10",  "federalist_01-10_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-11-20", "federalist_11-20_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-21-30", "federalist_21-30_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-31-40", "federalist_31-40_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-41-50", "federalist_41-50_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-51-60", "federalist_51-60_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-61-70", "federalist_61-70_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-71-80", "federalist_71-80_raw.html"),
    ("https://guides.loc.gov/federalist-papers/text-81-85", "federalist_81-85_raw.html"),
]

def log(msg):
    print(msg)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    open(LOG_PATH, "a", encoding="utf-8").write(msg + "\n")

def diagnose():
    log("=== checking connectivity ===")
    try:
        r = requests.get("https://www.loc.gov", timeout=TIMEOUT)
        log("loc.gov reachable: HTTP " + str(r.status_code))
        return True
    except Exception as e:
        log("FAILED to reach loc.gov: " + repr(e))
        return False

def clean(raw):
    t = re.sub("<script.*?</script>", "", raw, flags=re.S)
    t = re.sub("<style.*?</style>", "", t, flags=re.S)
    t = re.sub("<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub("[ \t]+", " ", t)
    t = re.sub("\n\s*\n+", "\n\n", t)
    return t.strip()

def fetch_one(url, filename):
    out_path = os.path.join(OUT_DIR, filename)
    txt_path = out_path.replace("_raw.html", "_extracted.txt")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log("SKIP (already have): " + filename)
        return True
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log("Fetching " + url + " (attempt " + str(attempt) + ")...")
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            os.makedirs(OUT_DIR, exist_ok=True)
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
    if not diagnose():
        sys.exit(1)
    log("=== fetching into " + OUT_DIR + " ===")
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
