-- New Public Systems — Living Corpus
-- Run this in Supabase SQL Editor: https://supabase.com → SQL Editor

-- Submissions table
CREATE TABLE IF NOT EXISTS submissions (
  id                UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  doc_id            INTEGER     NOT NULL,
  doc_title         TEXT,
  response_text     TEXT        NOT NULL,
  submit_template   TEXT,
  first_name        TEXT,          -- NULL if anonymous or under 13
  age_range         TEXT        NOT NULL
                    CHECK (age_range IN ('under_13','13_17','18_24','25_34','35_49','50_plus')),
  installation_name TEXT        DEFAULT 'New York, NY',
  installation_lat  NUMERIC(9,6),
  installation_lng  NUMERIC(9,6),
  consented         BOOLEAN     DEFAULT TRUE,
  submitted_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for querying by document
CREATE INDEX IF NOT EXISTS idx_submissions_doc_id ON submissions(doc_id);

-- Row Level Security: public inserts, authenticated reads
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

-- Anyone can insert (installation visitors)
DROP POLICY IF EXISTS "Allow public inserts" ON submissions;
CREATE POLICY "Allow public inserts"
  ON submissions FOR INSERT
  WITH CHECK (true);

-- Only authenticated users (you) can read
DROP POLICY IF EXISTS "Allow authenticated reads" ON submissions;
CREATE POLICY "Allow authenticated reads"
  ON submissions FOR SELECT
  USING (auth.role() = 'authenticated');

-- Useful views
CREATE OR REPLACE VIEW submissions_by_doc AS
  SELECT
    doc_id,
    doc_title,
    COUNT(*)              AS total,
    COUNT(first_name)     AS named_count,
    MIN(submitted_at)     AS first_submission,
    MAX(submitted_at)     AS latest_submission
  FROM submissions
  GROUP BY doc_id, doc_title
  ORDER BY doc_id;

-- To export all submissions as CSV: Table Editor → Export
