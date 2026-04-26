#!/usr/bin/env python3
"""Seed deterministic manual-testing data into the configured database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal, init_db
from app.seed import seed_test_data


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        result = seed_test_data(db)
    finally:
        db.close()
    status = "inserted" if result["inserted"] else "skipped (already seeded)"
    print(f"Test data seed {status}.")


if __name__ == "__main__":
    main()
