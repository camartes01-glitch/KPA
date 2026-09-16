"""
Verification script: test Alembic upgrade from a clean empty database to head.
"""
import os
import sys
from pathlib import Path

# Add backend root to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import sqlite3
from alembic.config import Config
from alembic import command

test_db_path = backend_dir / "test_fresh_zero.db"
if test_db_path.exists():
    test_db_path.unlink()

print(f"Testing zero-database migration on: {test_db_path}")

alembic_cfg = Config(str(backend_dir / "alembic.ini"))
alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path.as_posix()}")

# Run migration to head
command.upgrade(alembic_cfg, "head")

# Inspect database
conn = sqlite3.connect(test_db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
print("Tables created:")
for t in sorted(tables):
    cursor.execute(f"PRAGMA table_info({t})")
    cols = [col[1] for col in cursor.fetchall()]
    print(f"  - {t} ({len(cols)} columns)")

expected_tables = {
    "districts",
    "talukas",
    "users",
    "device_sessions",
    "otp_verifications",
    "members",
    "nominees",
    "welfare_events",
    "welfare_contributions",
    "payments",
    "autopay_mandates",
    "notifications",
    "audit_logs",
    "alembic_version",
}

missing = expected_tables - set(tables)
if missing:
    print(f"FAIL: Missing tables: {missing}")
    sys.exit(1)

cursor.execute("SELECT version_num FROM alembic_version")
current_rev = cursor.fetchone()[0]
print(f"Alembic version in DB: {current_rev}")

# Clean up
conn.close()
test_db_path.unlink()
print("SUCCESS: Zero-database Alembic migration verified completely!")
