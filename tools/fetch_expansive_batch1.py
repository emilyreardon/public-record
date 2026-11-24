import os, sys, time, re, html, requests

BASE = os.path.join(os.getcwd(), "new-public-systems-corpus", "_raw_expansive")
LOG_PATH = os.path.join(os.getcwd(), "new-public-systems-corpus", "_fetch_log.txt")
TIMEOUT = 20
MAX_RETRIES = 3
BACKOFF = 3

HTML_PAGES = [
    ("https://www.nps.gov/wori/learn/historyculture/declaration-of-sentiments.htm", "declaration_of_sentiments_raw.html"),
    ("https://teachingamericanhistory.org/document/what-to-the-slave-is-the-fourth-of-july-3/", "douglass_fourth_of_july_raw.html"),
    ("https://teachingamericanhistory.org/document/aint-i-a-woman/", "sojourner_truth_raw.html"),
    ("https://teachingamericanhistory.org/document/i-will-fight-no-more-forever/", "chief_joseph_surrender_raw.html"),
    ("https://avalon.law.yale.edu/19th_century/nt001.asp", "fort_laramie_treaty_1868_raw.html"),
    ("https://www.law.cornell.edu/supremecourt/text/60/393", "dred_scott_raw.html"),
    ("https://www.law.cornell.edu/supremecourt/text/163/537", "plessy_v_ferguson_raw.html"),
    ("https://www.law.cornell.edu/supremecourt/text/323/214", "korematsu_raw.html"),
    ("https://www.archives.gov/milestone-documents/executive-order-9066", "eo_9066_raw.html"),
    ("https://www.archives.gov/milestone-documents/executive-order-8802", "eo_8802_raw.html"),
]

PDF_PAGES = [
    ("https://www.govinfo.gov/content/pkg/STATUTE-7/pdf/STATUTE-7-Pg478.pdf", "treaty_new_echota_1835_raw.pdf"),
]

def log(msg):
    print(msg)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    open(LOG_PATH, "a", encoding="utf-8").write(msg + "\n")

def diagnose():
    log("=== checking connectivity ===")
    ok = True
    for host in ["https://www.nps.gov", "https://teachingamericanhistory.org", "https://avalon.law.yale.edu", "https://www.law.cornell.edu", "https://www.archives.gov", "https://www.govinfo.gov"]:
        try:
            r = requests.get(host, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
            log(host + " reachable: HTTP " + str(r.status_code))
        except Exception as e:
            log(host + " FAILED: " + repr(e))
            ok = False
    return ok

def clean(raw):
    t = re.sub("<script.*?</script>", "", raw, flags=re.S)
    t = re.sub("<style.*?</style>", "", t, flags=re.S)
    t = re.sub("<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub("[ \t]+", " ", t)
    t = re.sub("\n\\s*\n+", "\n\n", t)
    return t.strip()

def fetch_html(url, filename):
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

def fetch_pdf(url, filename):
    out_path = os.path.join(BASE, filename)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log("SKIP (already have): " + filename)
        return True
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log("Fetching PDF " + url + " (attempt " + str(attempt) + ")...")
            r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            os.makedirs(BASE, exist_ok=True)
            open(out_path, "wb").write(r.content)
            log("OK: saved " + filename + " (" + str(len(r.content)) + " bytes)")
            return True
        except Exception as e:
            log("  attempt " + str(attempt) + " failed: " + repr(e))
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF * attempt)
    log("FAILED after retries: " + url)
    return False

def main():
    if not diagnose():
        log("WARNING: some hosts unreachable, continuing anyway for the ones that work")
    log("=== fetching expansive batch 1 into " + BASE + " ===")
    results = []
    for url, filename in HTML_PAGES:
        ok = fetch_html(url, filename)
        results.append((filename, ok))
        time.sleep(1)
    for url, filename in PDF_PAGES:
        ok = fetch_pdf(url, filename)
        results.append((filename, ok))
        time.sleep(1)
    log("=== summary ===")
    for filename, ok in results:
        log(("OK  " if ok else "FAIL") + "  " + filename)
    log("done")

main()
