#!/usr/bin/env python3
"""
Diagnose and fix the New Public Systems Supabase submissions table.
Run from the new-public-systems-project folder:
    python3 supabase_fix.py
"""

import urllib.request, urllib.error, json, re, sys, os

# ── 1. Pull credentials from submit.html ─────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
html_path  = os.path.join(script_dir, 'submit.html')

with open(html_path) as f:
    html = f.read()

url_m = re.search(r"SUPABASE_URL:\s*'([^']+)'", html)
key_m = re.search(r"SUPABASE_ANON_KEY:\s*'([^']+)'", html)

if not url_m or not key_m:
    print("ERROR: Could not find SUPABASE_URL or SUPABASE_ANON_KEY in submit.html")
    sys.exit(1)

SUPABASE_URL  = url_m.group(1).rstrip('/')
ANON_KEY      = key_m.group(1)

print(f"Supabase URL : {SUPABASE_URL}")
print(f"Anon key     : {ANON_KEY[:40]}...")
print()

# ── 2. Helper ─────────────────────────────────────────────────────────────────
def request(method, path, body=None, key=None):
    k = key or ANON_KEY
    req = urllib.request.Request(
        SUPABASE_URL + path,
        data=json.dumps(body).encode() if body else None,
        headers={
            'Content-Type':  'application/json',
            'apikey':        k,
            'Authorization': f'Bearer {k}',
            'Prefer':        'return=minimal',
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as ex:
        return 0, str(ex)

# ── 3. Test anon insert (exact same payload the form sends) ───────────────────
print("── TEST: anon insert ─────────────────────────────────────────────────")
test_payload = {
    "doc_id":            1,
    "doc_title":         "Declaration of Independence",
    "response_text":     "SUPABASE_DIAGNOSTIC_TEST — delete me",
    "submit_template":   None,
    "first_name":        None,
    "age_range":         "18_24",
    "installation_name": "test",
    "installation_lat":  None,
    "installation_lng":  None,
    "consented":         True,
    "ui_language":       "en",
}

status, body = request('POST', '/rest/v1/submissions', test_payload)
print(f"Status : {status}")
print(f"Body   : {body[:500]}")
print()

if status in (200, 201, 204):
    print("✓ Insert succeeded! The form should be working.")
    print("  (A test row was inserted — delete it from your Supabase table editor.)")
    sys.exit(0)

# ── 4. Diagnose ───────────────────────────────────────────────────────────────
print("── DIAGNOSIS ─────────────────────────────────────────────────────────")

if status == 0:
    print("✗ Could not reach Supabase at all.")
    print("  → Check your internet connection and that the URL is correct.")
    sys.exit(1)

if status == 401:
    print("✗ 401 Unauthorized — anon key rejected.")
    print("  → In Supabase: Settings → API → copy the 'anon public' key and update CONFIG.SUPABASE_ANON_KEY in submit.html")
    sys.exit(1)

if status == 404 or ('"relation" not found' in body or 'does not exist' in body and 'submissions' in body):
    print("✗ Table 'submissions' does not exist.")
    print("  → Run this SQL in Supabase → SQL Editor:")
    print()
    print(CREATE_SQL)
    sys.exit(1)

if status == 403 or 'permission denied' in body.lower() or 'violates row-level' in body.lower():
    print("✗ 403 / RLS blocking inserts.")
    print("  This usually means the insert policy is missing or wrong.")

    # Ask for service role key to fix automatically
    print()
    print("To fix automatically, paste your SERVICE ROLE key (Supabase → Settings → API → service_role secret):")
    try:
        service_key = input("Service role key (or press Enter to skip): ").strip()
    except EOFError:
        service_key = ''

    if service_key:
        print()
        print("Applying RLS fix via service role key...")

        # Try dropping and recreating the policy
        fix_sql_statements = [
            "DROP POLICY IF EXISTS \"public can insert\" ON submissions;",
            "ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;",
            "CREATE POLICY \"public can insert\" ON submissions FOR INSERT TO anon WITH CHECK (true);",
        ]

        for stmt in fix_sql_statements:
            s, b = request('POST', '/rest/v1/rpc/exec_sql',
                           {"query": stmt}, key=service_key)
            print(f"  {stmt[:60]}... → {s}")

        # Re-test
        print()
        print("Re-testing insert...")
        status2, body2 = request('POST', '/rest/v1/submissions', test_payload)
        print(f"Status: {status2}  Body: {body2[:200]}")
        if status2 in (200, 201, 204):
            print("✓ Fixed! Try submitting the form again.")
        else:
            print("✗ Still failing. Use the manual SQL below in Supabase SQL Editor.")
    else:
        print()
        print("Manual fix — paste into Supabase → SQL Editor → New query:")

    print()
    print("""-- RLS fix
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS \"public can insert\" ON submissions;
CREATE POLICY \"public can insert\"
  ON submissions FOR INSERT
  TO anon
  WITH CHECK (true);""")
    sys.exit(0)

if status == 400:
    print("✗ 400 Bad Request — likely a column mismatch.")
    print(f"  Supabase says: {body}")
    print()

    # Try to identify missing column
    col_match = re.search(r'column ["\']?(\w+)["\']? of relation', body)
    if col_match:
        missing = col_match.group(1)
        print(f"  Missing column: {missing}")
        type_map = {
            'doc_id': 'integer', 'doc_title': 'text', 'response_text': 'text',
            'submit_template': 'text', 'first_name': 'text', 'age_range': 'text',
            'installation_name': 'text', 'installation_lat': 'double precision',
            'installation_lng': 'double precision', 'consented': 'boolean',
            'ui_language': 'text',
        }
        col_type = type_map.get(missing, 'text')
        print(f"  Fix: ALTER TABLE submissions ADD COLUMN IF NOT EXISTS {missing} {col_type};")
    else:
        print("  Run this in Supabase SQL Editor to add all expected columns:")
        print()
        print("""ALTER TABLE submissions
  ADD COLUMN IF NOT EXISTS doc_id            integer,
  ADD COLUMN IF NOT EXISTS doc_title         text,
  ADD COLUMN IF NOT EXISTS response_text     text,
  ADD COLUMN IF NOT EXISTS submit_template   text,
  ADD COLUMN IF NOT EXISTS first_name        text,
  ADD COLUMN IF NOT EXISTS age_range         text,
  ADD COLUMN IF NOT EXISTS installation_name text,
  ADD COLUMN IF NOT EXISTS installation_lat  double precision,
  ADD COLUMN IF NOT EXISTS installation_lng  double precision,
  ADD COLUMN IF NOT EXISTS consented         boolean default true,
  ADD COLUMN IF NOT EXISTS ui_language       text;""")
    sys.exit(1)

# ── 5. Catch-all ──────────────────────────────────────────────────────────────
print(f"✗ Unexpected error {status}.")
print(f"  Body: {body}")
print()
print("Full table + RLS setup SQL to try in Supabase SQL Editor:")
print()
print("""CREATE TABLE IF NOT EXISTS submissions (
  id                bigint generated always as identity primary key,
  created_at        timestamptz default now(),
  doc_id            integer,
  doc_title         text,
  response_text     text,
  submit_template   text,
  first_name        text,
  age_range         text,
  installation_name text,
  installation_lat  double precision,
  installation_lng  double precision,
  consented         boolean default true,
  ui_language       text
);
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS \"public can insert\" ON submissions;
CREATE POLICY \"public can insert\"
  ON submissions FOR INSERT TO anon WITH CHECK (true);
DROP POLICY IF EXISTS \"authenticated can read\" ON submissions;
CREATE POLICY \"authenticated can read\"
  ON submissions FOR SELECT TO authenticated USING (true);""")
