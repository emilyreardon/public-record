#!/usr/bin/env python3
"""
Fetch ratification debate excerpts for the 19th, 24th, and 26th Amendments
from govinfo.gov bound Congressional Record PDFs.

NOTE on 13th and 15th Amendments:
  Those debates are in the Congressional Globe (1864-1865 and 1869), which
  exists only as scanned images on congress.gov -- not accessible as text PDFs.
  See fetch_13th_15th_options.md in this folder for alternative sources.

Run from your project root:
  python fetch_ratification_debates.py

Requires: pip install requests pypdf
Writes to: new-public-systems-corpus/expansive/congressional_debates/
Logs to:   new-public-systems-corpus/_fetch_log.txt
"""

import os
import sys
import time
import datetime
import requests

try:
    from pypdf import PdfReader
    from io import BytesIO
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf")
    sys.exit(1)

LOG = "new-public-systems-corpus/_fetch_log.txt"
OUT_DIR = "new-public-systems-corpus/expansive/congressional_debates"
MAX_RETRIES = 3
RETRY_DELAY = 5


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[{}] {}".format(ts, msg)
    print(line)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def fetch_pdf(url, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            log("Fetching (attempt {}): {}".format(attempt, url))
            r = requests.get(url, timeout=90, headers={
                "User-Agent": "new-public-systems-corpus-builder/1.0"
            })
            r.raise_for_status()
            log("OK: {} bytes".format(len(r.content)))
            return r.content
        except Exception as e:
            log("ERROR attempt {}: {}".format(attempt, e))
            if attempt < retries:
                time.sleep(RETRY_DELAY)
    return None


def extract_text(pdf_bytes, filename):
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        combined = "\n\n".join(pages)
        log("Extracted {} chars from {}".format(len(combined), filename))
        return combined
    except Exception as e:
        log("PDF extraction error for {}: {}".format(filename, e))
        return ""


def write_doc(filename, header, raw_text):
    path = os.path.join(OUT_DIR, filename)
    if os.path.exists(path):
        log("SKIP (exists): {}".format(path))
        return False
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header.strip())
        f.write("\n\n")
        if raw_text.strip():
            f.write(raw_text.strip())
            f.write("\n")
        else:
            f.write("[WARNING: No text extracted. PDF may be image-only. "
                    "Open the URL manually and copy text.]\n")
    log("WROTE: {}".format(path))
    return True


# ---------------------------------------------------------------------------
# URL confidence:
#   CONFIRMED = appeared verbatim in govinfo.gov search results
#   ESTIMATED = same collection + right date range; file number is a guess
#
# If an estimated URL fails or returns bad text, browse the ALT_PATTERN URL
# to find the correct file, download manually, and run:
#   python extract_pdf_text.py <file.pdf> > output.txt
# ---------------------------------------------------------------------------

DOCUMENTS = [

    # ------------------------------------------------------------------
    # 19TH AMENDMENT: Women's right to vote
    # Senate passed June 4, 1919. House passed May 21, 1919 (304-89).
    # Ratified August 18, 1920.
    # ------------------------------------------------------------------
    {
        "filename": "19th_amendment_senate_debate_1919.md",
        "url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1919-pt2-v58/pdf/GPO-CRECB-1919-pt2-v58-6-1.pdf",
        "url_confidence": "CONFIRMED",
        "header": """---
title: Senate Debate on the Nineteenth Amendment (June 4, 1919)
tier: expansive
doc_type: congressional_debate
date: 1919-06-04
citation: Congressional Record, 66th Congress, 1st Session, vol. 58, pt. 2 (June 1919).
source_url: https://www.govinfo.gov/content/pkg/GPO-CRECB-1919-pt2-v58/pdf/GPO-CRECB-1919-pt2-v58-6-1.pdf
source_name: U.S. Government Publishing Office, Bound Congressional Record
source_type: primary_government
provenance_note: >
  Extracted from the bound Congressional Record, 66th Congress, 1st Session, vol. 58
  (1919), pt. 2, via govinfo.gov. Senate passed June 4, 1919. House passed May 21,
  1919 (304-89). Ratified August 18, 1920. Text extracted via pypdf; minor OCR
  artifacts possible.
retrieval_tags: [19th amendment, women's suffrage, vote, 1919, senate, congressional record]
paired_with: []
mobile_piece:
verified: false
---

Source: Congressional Record, 66th Congress, 1st Session, vol. 58, pt. 2 (June 1919).
govinfo.gov: https://www.govinfo.gov/content/pkg/GPO-CRECB-1919-pt2-v58/pdf/GPO-CRECB-1919-pt2-v58-6-1.pdf

Senate passed the Nineteenth Amendment on June 4, 1919.
House passed May 21, 1919 (304-89). Ratified August 18, 1920.

""",
    },

    {
        "filename": "19th_amendment_house_debate_1919.md",
        "url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1919-pt1-v58/pdf/GPO-CRECB-1919-pt1-v58-1-2.pdf",
        "url_confidence": "ESTIMATED",
        # ALT: Browse https://www.govinfo.gov/app/details/GPO-CRECB-1919-pt1-v58
        # and find the PDF containing May 21, 1919 House proceedings.
        "header": """---
title: House Debate on the Nineteenth Amendment (May 21, 1919)
tier: expansive
doc_type: congressional_debate
date: 1919-05-21
citation: Congressional Record, 66th Congress, 1st Session, vol. 58, pt. 1 (May 1919).
source_url: https://www.govinfo.gov/content/pkg/GPO-CRECB-1919-pt1-v58/pdf/GPO-CRECB-1919-pt1-v58-1-2.pdf
source_name: U.S. Government Publishing Office, Bound Congressional Record
source_type: primary_government
provenance_note: >
  Extracted from the bound Congressional Record, 66th Congress, 1st Session, vol. 58
  (1919), pt. 1, via govinfo.gov. House passed May 21, 1919 (304-89). Senate passed
  June 4, 1919. Ratified August 18, 1920. URL is estimated -- if text is wrong browse
  govinfo.gov/app/details/GPO-CRECB-1919-pt1-v58 to find the May 21 file.
retrieval_tags: [19th amendment, women's suffrage, vote, 1919, house, congressional record]
paired_with: []
mobile_piece:
verified: false
---

Source: Congressional Record, 66th Congress, 1st Session, vol. 58, pt. 1 (May 1919).
govinfo.gov: https://www.govinfo.gov/app/details/GPO-CRECB-1919-pt1-v58

House passed the Nineteenth Amendment on May 21, 1919 (304-89).
Senate passed June 4, 1919. Ratified August 18, 1920.

""",
    },

    # ------------------------------------------------------------------
    # 24TH AMENDMENT: Abolition of poll tax
    # Senate passed March 27, 1962 (77-16).
    # House passed August 27, 1962 (294-86).
    # Ratified January 23, 1964.
    # ------------------------------------------------------------------
    {
        "filename": "24th_amendment_senate_debate_1962.md",
        "url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1962-pt4/pdf/GPO-CRECB-1962-pt4-9-1.pdf",
        "url_confidence": "CONFIRMED",
        "header": """---
title: Senate Debate on the Twenty-Fourth Amendment (March 27, 1962)
tier: expansive
doc_type: congressional_debate
date: 1962-03-27
citation: Congressional Record, 87th Congress, 2nd Session, vol. 108, pt. 4 (March 1962).
source_url: https://www.govinfo.gov/content/pkg/GPO-CRECB-1962-pt4/pdf/GPO-CRECB-1962-pt4-9-1.pdf
source_name: U.S. Government Publishing Office, Bound Congressional Record
source_type: primary_government
provenance_note: >
  Extracted from the bound Congressional Record, 87th Congress, 2nd Session, vol. 108
  (1962), pt. 4, via govinfo.gov. Senate passed the Twenty-Fourth Amendment on March 27,
  1962 (77-16) after surviving a filibuster. House passed August 27, 1962 (294-86).
  Ratified January 23, 1964. Five states maintained poll taxes at passage: Virginia,
  Alabama, Mississippi, Arkansas, and Texas.
retrieval_tags: [24th amendment, poll tax, voting rights, 1962, senate, congressional record]
paired_with: []
mobile_piece:
verified: false
---

Source: Congressional Record, 87th Congress, 2nd Session, vol. 108, pt. 4 (March 1962).
govinfo.gov: https://www.govinfo.gov/content/pkg/GPO-CRECB-1962-pt4/pdf/GPO-CRECB-1962-pt4-9-1.pdf

Senate passed the Twenty-Fourth Amendment on March 27, 1962 (77-16) after a filibuster.
House passed August 27, 1962 (294-86). Ratified January 23, 1964.
States with poll taxes: Virginia, Alabama, Mississippi, Arkansas, Texas.

""",
    },

    {
        "filename": "24th_amendment_house_debate_1962.md",
        "url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1962-pt12/pdf/GPO-CRECB-1962-pt12-1-2.pdf",
        "url_confidence": "ESTIMATED",
        # ALT: Browse https://www.govinfo.gov/app/collection/crecb_gpo/1962
        # Part 14 = Sept 13, so August 27 is probably in pt12 or pt13.
        "alt_url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1962-pt13/pdf/GPO-CRECB-1962-pt13-1-2.pdf",
        "header": """---
title: House Debate on the Twenty-Fourth Amendment (August 27, 1962)
tier: expansive
doc_type: congressional_debate
date: 1962-08-27
citation: Congressional Record, 87th Congress, 2nd Session, vol. 108, pt. 12 (August 1962).
source_url: https://www.govinfo.gov/content/pkg/GPO-CRECB-1962-pt12/pdf/GPO-CRECB-1962-pt12-1-2.pdf
source_name: U.S. Government Publishing Office, Bound Congressional Record
source_type: primary_government
provenance_note: >
  Extracted from the bound Congressional Record, 87th Congress, 2nd Session, vol. 108
  (1962), pt. 12 (estimated), via govinfo.gov. House passed August 27, 1962 (294-86).
  URL is estimated -- if text is wrong browse govinfo.gov/app/collection/crecb_gpo/1962
  to find the August 27 file.
retrieval_tags: [24th amendment, poll tax, voting rights, 1962, house, congressional record]
paired_with: []
mobile_piece:
verified: false
---

Source: Congressional Record, 87th Congress, 2nd Session, vol. 108, pt. 12 (August 1962).
govinfo.gov: https://www.govinfo.gov/app/collection/crecb_gpo/1962

House passed the Twenty-Fourth Amendment on August 27, 1962 (294-86).
Senate had passed March 27, 1962 (77-16). Ratified January 23, 1964.

""",
    },

    # ------------------------------------------------------------------
    # 26TH AMENDMENT: Voting age lowered to 18
    # Senate passed March 10, 1971 (unanimous).
    # House passed March 23, 1971 (401-19).
    # Ratified July 1, 1971 (fastest ratification ever: 83 days).
    # ------------------------------------------------------------------
    {
        "filename": "26th_amendment_house_debate_1971.md",
        "url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1971-pt6/pdf/GPO-CRECB-1971-pt6-5-2.pdf",
        "url_confidence": "CONFIRMED",
        "header": """---
title: House Debate on the Twenty-Sixth Amendment (March 23, 1971)
tier: expansive
doc_type: congressional_debate
date: 1971-03-23
citation: Congressional Record, 92nd Congress, 1st Session, vol. 117, pt. 6 (March 1971).
source_url: https://www.govinfo.gov/content/pkg/GPO-CRECB-1971-pt6/pdf/GPO-CRECB-1971-pt6-5-2.pdf
source_name: U.S. Government Publishing Office, Bound Congressional Record
source_type: primary_government
provenance_note: >
  Extracted from the bound Congressional Record, 92nd Congress, 1st Session, vol. 117
  (1971), pt. 6, via govinfo.gov. House passed the Twenty-Sixth Amendment on March 23,
  1971 (401-19). Senate had passed March 10, 1971 (unanimous). Ratified July 1, 1971 --
  the shortest ratification period of any amendment (83 days). Driven in part by the
  Vietnam War: young men drafted at 18 could not vote.
retrieval_tags: [26th amendment, voting age, 18, 1971, house, congressional record, vietnam]
paired_with: []
mobile_piece:
verified: false
---

Source: Congressional Record, 92nd Congress, 1st Session, vol. 117, pt. 6 (March 1971).
govinfo.gov: https://www.govinfo.gov/content/pkg/GPO-CRECB-1971-pt6/pdf/GPO-CRECB-1971-pt6-5-2.pdf

House passed the Twenty-Sixth Amendment on March 23, 1971 (401-19).
Senate passed March 10, 1971 (unanimous). Ratified July 1, 1971 (83 days -- fastest ever).

""",
    },

    {
        "filename": "26th_amendment_senate_debate_1971.md",
        "url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1971-pt5/pdf/GPO-CRECB-1971-pt5-2.pdf",
        "url_confidence": "ESTIMATED",
        # ALT: pt5-5 confirmed = March 15. March 10 is likely pt5-1 or pt5-2.
        "alt_url": "https://www.govinfo.gov/content/pkg/GPO-CRECB-1971-pt5/pdf/GPO-CRECB-1971-pt5-1.pdf",
        "header": """---
title: Senate Debate on the Twenty-Sixth Amendment (March 10, 1971)
tier: expansive
doc_type: congressional_debate
date: 1971-03-10
citation: Congressional Record, 92nd Congress, 1st Session, vol. 117, pt. 5 (March 1971).
source_url: https://www.govinfo.gov/content/pkg/GPO-CRECB-1971-pt5/pdf/GPO-CRECB-1971-pt5-2.pdf
source_name: U.S. Government Publishing Office, Bound Congressional Record
source_type: primary_government
provenance_note: >
  Extracted from the bound Congressional Record, 92nd Congress, 1st Session, vol. 117
  (1971), pt. 5, via govinfo.gov. Senate passed the Twenty-Sixth Amendment on March 10,
  1971 (unanimous). House passed March 23, 1971 (401-19). Ratified July 1, 1971.
  URL is estimated (pt5-5 confirmed = March 15; March 10 likely in pt5-1 or pt5-2).
  If text is wrong browse govinfo.gov/app/details/GPO-CRECB-1971-pt5.
retrieval_tags: [26th amendment, voting age, 18, 1971, senate, congressional record, vietnam]
paired_with: []
mobile_piece:
verified: false
---

Source: Congressional Record, 92nd Congress, 1st Session, vol. 117, pt. 5 (March 1971).
govinfo.gov: https://www.govinfo.gov/app/details/GPO-CRECB-1971-pt5

Senate passed the Twenty-Sixth Amendment on March 10, 1971 (unanimous).
House passed March 23, 1971 (401-19). Ratified July 1, 1971 (83 days -- fastest ever).

""",
    },

]


def main():
    log("=== fetch_ratification_debates.py started ===")
    os.makedirs(OUT_DIR, exist_ok=True)
    success = 0
    failed = []

    for doc in DOCUMENTS:
        filename = doc["filename"]
        out_path = os.path.join(OUT_DIR, filename)

        if os.path.exists(out_path):
            log("SKIP (exists): {}".format(out_path))
            success += 1
            continue

        confidence = doc.get("url_confidence", "UNKNOWN")
        log("URL confidence: {} -- {}".format(confidence, doc["url"]))

        pdf_bytes = fetch_pdf(doc["url"])

        if pdf_bytes is None and "alt_url" in doc:
            log("Primary URL failed. Trying alt_url...")
            alt = doc["alt_url"]
            pdf_bytes = fetch_pdf(alt)

        if pdf_bytes is None:
            log("FAILED: {}".format(filename))
            log("  Manual fallback: open {} in browser, download PDF,".format(doc["url"]))
            log("  extract text, and prepend the header block from this script.")
            failed.append(filename)
            continue

        raw_text = extract_text(pdf_bytes, filename)
        write_doc(filename, doc["header"], raw_text)
        success += 1

    log("=== done: {}/{} attempted ===".format(success + len(failed), len(DOCUMENTS)))
    if failed:
        log("Needs manual fetch: {}".format(", ".join(failed)))


if __name__ == "__main__":
    main()
