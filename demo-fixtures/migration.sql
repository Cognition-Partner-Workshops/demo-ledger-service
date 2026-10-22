-- customize-demo: repo glob rule applied
-- demo-fixtures/migration.sql: fixture so the repo-side glob rule has a .sql file to match.
CREATE TABLE demo_fixture (
    id INTEGER PRIMARY KEY,
    note TEXT NOT NULL
);

-- Speeds up fixture lookups by note.
CREATE INDEX idx_demo_fixture_note ON demo_fixture(note);
