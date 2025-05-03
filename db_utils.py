from pathlib import Path
import sqlite3
from functools import lru_cache

DB_PATH = Path("experiments.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS trials (
    id         TEXT,
    provider   TEXT,
    model      TEXT,
    num_facts  INTEGER,
    k          INTEGER,
    trial_idx  INTEGER,
    seq_acc    REAL,
    tok_acc    REAL,
    flaw       INTEGER,
    prompt     TEXT,
    response   TEXT,
    expected   TEXT,
    PRIMARY KEY (id, trial_idx)
);
CREATE INDEX IF NOT EXISTS idx_provider_k ON trials (provider, k);
"""

@lru_cache(maxsize=1)
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.executescript(SCHEMA)
    return conn
