CREATE TABLE IF NOT EXISTS legal_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    country_code TEXT,
    article TEXT,
    text TEXT NOT NULL,
    source_url TEXT,
    language TEXT NOT NULL DEFAULT 'en',
    effective_from TEXT,
    effective_to TEXT,
    verified INTEGER NOT NULL DEFAULT 0 CHECK (verified IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_legal_sources_jurisdiction
    ON legal_sources (jurisdiction);

CREATE INDEX IF NOT EXISTS idx_legal_sources_country_code
    ON legal_sources (country_code);

CREATE INDEX IF NOT EXISTS idx_legal_sources_verified
    ON legal_sources (verified DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_legal_sources_effective_dates
    ON legal_sources (effective_from, effective_to);

CREATE TABLE IF NOT EXISTS research_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    query TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_research_history_case_id
    ON research_history (case_id, created_at DESC);

CREATE TABLE IF NOT EXISTS argument_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    argument TEXT NOT NULL,
    evidence TEXT NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'unverified'
        CHECK (verification_status IN ('unverified', 'verified', 'disputed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_argument_evidence_status
    ON argument_evidence (verification_status);

PRAGMA user_version = 1;
