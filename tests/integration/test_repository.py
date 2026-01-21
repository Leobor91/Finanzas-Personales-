import os
from pathlib import Path
import tempfile

from src.infrastructure.database.sqlite_adapter import SQLiteMovementRepository
from src.core.domain.entities import Movement


def test_db_creation_and_save(tmp_path):
    db_file = tmp_path / "test_finance.db"
    repo = SQLiteMovementRepository(db_path=db_file)
    m = Movement(date="2024-01-15", type="Ingreso", amount=50, category="Test", description="Desc")
    rowid = repo.save(m)
    assert isinstance(rowid, int)
    repo.close()
    assert db_file.exists()

    # verify content
    import sqlite3

    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("SELECT date, type, amount, category, description FROM movements WHERE id=?", (rowid,))
    row = cur.fetchone()
    conn.close()
    assert row[0] == "2024-01-15"
    assert row[1] == "Ingreso"
    assert row[2] == 50.0
