import sqlite3
from pathlib import Path
from typing import Optional

from src.core.ports.repository import MovementRepositoryInterface

DB_FILENAME = Path.cwd() / "finance_app.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Ingreso','Gasto')),
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'COP',
    fx_rate REAL,
    category TEXT NOT NULL,
    description TEXT
);
"""

CREATE_CATEGORIES_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('Ingreso','Gasto')),
    name TEXT NOT NULL UNIQUE,
    icon TEXT
);
"""


class SQLiteMovementRepository(MovementRepositoryInterface):
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DB_FILENAME
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        cur.execute(CREATE_CATEGORIES_SQL)
        # Ensure icon column exists for older DBs (simple migration)
        try:
            cur.execute("PRAGMA table_info(categories)")
            cols = [r[1] for r in cur.fetchall()]
            if 'icon' not in cols:
                cur.execute("ALTER TABLE categories ADD COLUMN icon TEXT")
        except Exception:
            pass
        # Ensure movements table has currency and fx_rate columns for older DBs
        try:
            cur.execute("PRAGMA table_info(movements)")
            mcols = [r[1] for r in cur.fetchall()]
            if 'currency' not in mcols:
                cur.execute("ALTER TABLE movements ADD COLUMN currency TEXT NOT NULL DEFAULT 'COP'")
            if 'fx_rate' not in mcols:
                cur.execute("ALTER TABLE movements ADD COLUMN fx_rate REAL")
        except Exception:
            pass
        self.conn.commit()

    def save(self, movement):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO movements (date, type, amount, currency, fx_rate, category, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (movement.date, movement.type, movement.amount, movement.currency, movement.fx_rate, movement.category, movement.description),
        )
        self.conn.commit()
        return cur.lastrowid

    def find_by_criteria(self, date_from=None, date_to=None, category=None):
        cur = self.conn.cursor()
        sql = "SELECT id, date, type, amount, currency, fx_rate, category, description FROM movements WHERE 1=1"
        params = []
        if date_from:
            sql += " AND date >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND date <= ?"
            params.append(date_to)
        if category:
            sql += " AND category LIKE ?"
            params.append(f"%{category}%")

        sql += " ORDER BY date DESC"
        cur.execute(sql, params)
        rows = cur.fetchall()
        # Map rows to dictionaries
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "date": r[1],
                "type": r[2],
                "amount": r[3],
                "currency": r[4],
                "fx_rate": r[5],
                "category": r[6],
                "description": r[7],
            })
        return results

    def get_monthly_aggregates(self, month: str, year: str):
        cur = self.conn.cursor()
        sql = "SELECT type, SUM(amount) as total FROM movements WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ? GROUP BY type"
        cur.execute(sql, (month, year))
        rows = cur.fetchall()
        # return dict type -> total
        return {r[0]: r[1] for r in rows}

    

    def get_expenses_by_category(self, year: str = None, month: str = None):
        cur = self.conn.cursor()
        if year and month:
            sql = "SELECT category, SUM(amount) as total FROM movements WHERE type = 'Gasto' AND strftime('%Y', date) = ? AND strftime('%m', date) = ? GROUP BY category ORDER BY total DESC"
            cur.execute(sql, (year, month))
        elif year:
            sql = "SELECT category, SUM(amount) as total FROM movements WHERE type = 'Gasto' AND strftime('%Y', date) = ? GROUP BY category ORDER BY total DESC"
            cur.execute(sql, (year,))
        else:
            sql = "SELECT category, SUM(amount) as total FROM movements WHERE type = 'Gasto' GROUP BY category ORDER BY total DESC"
            cur.execute(sql)
        rows = cur.fetchall()
        return [{"category": r[0], "total": r[1]} for r in rows]

    def get_yearly_aggregates(self, year: str):
        cur = self.conn.cursor()
        # We want totals per month and per type. Use strftime to extract month.
        sql = "SELECT strftime('%m', date) as m, type, SUM(amount) as total FROM movements WHERE strftime('%Y', date) = ? GROUP BY m, type"
        cur.execute(sql, (year,))
        rows = cur.fetchall()
        # Build dict: month -> { 'Ingreso': x, 'Gasto': y }
        result = {}
        for m, t, total in rows:
            if m not in result:
                result[m] = {}
            result[m][t] = total
        # Ensure all months present (01..12) even if zero
        for i in range(1,13):
            key = str(i).zfill(2)
            if key not in result:
                result[key] = { 'Ingreso': 0.0, 'Gasto': 0.0 }
            else:
                result[key].setdefault('Ingreso', 0.0)
                result[key].setdefault('Gasto', 0.0)
        return result

    def get_daily_aggregates(self, month: str, year: str):
        cur = self.conn.cursor()
        # Extract day with strftime('%d', date)
        sql = "SELECT strftime('%d', date) as d, type, SUM(amount) as total FROM movements WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ? GROUP BY d, type"
        cur.execute(sql, (month, year))
        rows = cur.fetchall()
        result = {}
        for d, t, total in rows:
            if d not in result:
                result[d] = {}
            result[d][t] = total
        # Determine maximum days for the month (account for 28-31). We'll fill days 01..max_day
        import calendar
        yr = int(year)
        mo = int(month)
        max_day = calendar.monthrange(yr, mo)[1]
        for i in range(1, max_day+1):
            key = str(i).zfill(2)
            if key not in result:
                result[key] = { 'Ingreso': 0.0, 'Gasto': 0.0 }
            else:
                result[key].setdefault('Ingreso', 0.0)
                result[key].setdefault('Gasto', 0.0)
        return result

    def get_top_expenses(self, month: str, year: str, limit: int = 5, category: str = None):
        cur = self.conn.cursor()
        sql = (
            "SELECT category, description, amount, date "
            "FROM movements "
            "WHERE type = 'Gasto' AND strftime('%m', date) = ? AND strftime('%Y', date) = ? "
        )
        params = [month, year]
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY amount DESC LIMIT ?"
        params.append(limit)
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        return [
            {"category": r[0], "description": r[1], "amount": r[2], "date": r[3]}
            for r in rows
        ]

    def close(self):
        self.conn.close()

    # Categories support
    def get_categories_by_type(self, type: str):
        cur = self.conn.cursor()
        sql = "SELECT id, name, icon FROM categories WHERE type = ? ORDER BY name"
        cur.execute(sql, (type,))
        rows = cur.fetchall()
        return [{"id": r[0], "name": r[1], "icon": r[2]} for r in rows]

    def add_category(self, type: str, name: str, icon: str = None):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO categories (type, name, icon) VALUES (?, ?, ?)", (type, name, icon))
            self.conn.commit()
            return cur.lastrowid
        except Exception:
            # If exists, return existing id
            cur.execute("SELECT id FROM categories WHERE name = ? AND type = ?", (name, type))
            r = cur.fetchone()
            return r[0] if r else None

    def list_all_categories(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, type, name, icon FROM categories ORDER BY type, name")
        rows = cur.fetchall()
        return [{"id": r[0], "type": r[1], "name": r[2], "icon": r[3]} for r in rows]

    def delete_category(self, category_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def update_category(self, category_id: int, new_name: str):
        cur = self.conn.cursor()
        try:
            # If icon provided in new_name (via signature change), handle new signature
            # The interface may pass icon separately; we'll accept new_name and ignore icon here
            cur.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, category_id))
            self.conn.commit()
            return cur.rowcount > 0
        except Exception:
            return False
