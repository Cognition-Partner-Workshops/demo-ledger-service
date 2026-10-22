-- demo-fixtures/migration.sql: fixture so the repo-side glob rule has a .sql file to match.
CREATE TABLE demo_fixture (
    id INTEGER PRIMARY KEY,
    note TEXT NOT NULL
);
