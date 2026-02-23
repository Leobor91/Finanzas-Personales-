import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, parse_qs, urlunparse
from typing import Optional

from src.core.ports.repository import MovementRepositoryInterface


CREATE_TABLES_SQL = (
    """
    CREATE TABLE IF NOT EXISTS movements (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('Ingreso','Gasto')),
        amount DOUBLE PRECISION NOT NULL,
        currency TEXT NOT NULL DEFAULT 'COP',
        fx_rate DOUBLE PRECISION,
        category TEXT NOT NULL,
        description TEXT,
        account TEXT
    );

    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        type TEXT NOT NULL CHECK (type IN ('Ingreso','Gasto')),
        name TEXT NOT NULL,
        icon TEXT,
        UNIQUE(type, name)
    );

    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        initial_balance DOUBLE PRECISION NOT NULL DEFAULT 0.0,
        currency TEXT NOT NULL DEFAULT 'COP'
    );

    CREATE TABLE IF NOT EXISTS transfers (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        from_account TEXT NOT NULL,
        to_account TEXT NOT NULL,
        amount DOUBLE PRECISION NOT NULL,
        currency TEXT NOT NULL DEFAULT 'COP',
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS denominations (
        id SERIAL PRIMARY KEY,
        value DOUBLE PRECISION NOT NULL UNIQUE,
        label TEXT
    );
    """
)


class PostgresMovementRepository(MovementRepositoryInterface):
    def __init__(self, database_url: Optional[str] = None):
        raw = database_url or os.environ.get('DATABASE_URL')
        if not raw:
            raise RuntimeError('DATABASE_URL not provided for Postgres adapter')

        # normalize scheme (postgres:// -> postgresql://)
        if raw.startswith('postgres://'):
            raw = raw.replace('postgres://', 'postgresql://', 1)

        # ensure sslmode is present by default for hosted providers
        p = urlparse(raw)
        qs = parse_qs(p.query or '')
        if 'sslmode' not in qs:
            new_query = p.query + ('&' if p.query else '') + 'sslmode=require'
            p = p._replace(query=new_query)
            raw = urlunparse(p)

        self.database_url = raw
        self._conn = psycopg2.connect(self.database_url)
        # alias for compatibility
        self.conn = self._conn
        self._conn.autocommit = True
        self._init_db()

    def _init_db(self):
        cur = self._conn.cursor()
        cur.execute(CREATE_TABLES_SQL)
        cur.close()

    def save(self, movement):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO movements (date, type, amount, currency, fx_rate, category, description, account) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (movement.date, movement.type, movement.amount, movement.currency, movement.fx_rate, movement.category, movement.description, getattr(movement, 'account', None)),
        )
        mid = cur.fetchone()[0]
        cur.close()
        return mid

    def find_by_criteria(self, date_from=None, date_to=None, category=None, type_=None):
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        sql = "SELECT id, to_char(date,'YYYY-MM-DD') as date, type, amount, currency, fx_rate, category, description, account FROM movements WHERE 1=1"
        params = []
        if date_from:
            sql += " AND date >= %s"
            params.append(date_from)
        if date_to:
            sql += " AND date <= %s"
            params.append(date_to)
        if category:
            sql += " AND category ILIKE %s"
            params.append(f"%{category}%")
        if type_:
            sql += " AND type = %s"
            params.append(type_)
        sql += " ORDER BY date DESC"
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        return [dict(r) for r in rows]

    def get_monthly_aggregates(self, month: str, year: str):
        cur = self._conn.cursor()
        sql = "SELECT type, SUM(amount) as total FROM movements WHERE to_char(date,'MM') = %s AND to_char(date,'YYYY') = %s GROUP BY type"
        cur.execute(sql, (month, year))
        rows = cur.fetchall()
        cur.close()
        return {r[0]: r[1] for r in rows}

    def get_expenses_by_category(self, year: str = None, month: str = None):
        cur = self._conn.cursor()
        if year and month:
            sql = "SELECT category, SUM(amount) as total FROM movements WHERE type = 'Gasto' AND to_char(date,'YYYY') = %s AND to_char(date,'MM') = %s GROUP BY category ORDER BY total DESC"
            cur.execute(sql, (year, month))
        elif year:
            sql = "SELECT category, SUM(amount) as total FROM movements WHERE type = 'Gasto' AND to_char(date,'YYYY') = %s GROUP BY category ORDER BY total DESC"
            cur.execute(sql, (year,))
        else:
            sql = "SELECT category, SUM(amount) as total FROM movements WHERE type = 'Gasto' GROUP BY category ORDER BY total DESC"
            cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return [{"category": r[0], "total": r[1]} for r in rows]

    def get_yearly_aggregates(self, year: str):
        cur = self._conn.cursor()
        sql = "SELECT to_char(date,'MM') as m, type, SUM(amount) as total FROM movements WHERE to_char(date,'YYYY') = %s GROUP BY m, type"
        cur.execute(sql, (year,))
        rows = cur.fetchall()
        result = {}
        for m, t, total in rows:
            if m not in result:
                result[m] = {}
            result[m][t] = total
        for i in range(1,13):
            key = str(i).zfill(2)
            if key not in result:
                result[key] = { 'Ingreso': 0.0, 'Gasto': 0.0 }
            else:
                result[key].setdefault('Ingreso', 0.0)
                result[key].setdefault('Gasto', 0.0)
        cur.close()
        return result

    def get_daily_aggregates(self, month: str, year: str):
        cur = self._conn.cursor()
        sql = "SELECT to_char(date,'DD') as d, type, SUM(amount) as total FROM movements WHERE to_char(date,'MM') = %s AND to_char(date,'YYYY') = %s GROUP BY d, type"
        cur.execute(sql, (month, year))
        rows = cur.fetchall()
        result = {}
        for d, t, total in rows:
            if d not in result:
                result[d] = {}
            result[d][t] = total
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
        cur.close()
        return result

    def get_top_expenses(self, month: str, year: str, limit: int = 5, category: str = None):
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        sql = (
            "SELECT category, description, amount, to_char(date,'YYYY-MM-DD') as date, account "
            "FROM movements WHERE type = 'Gasto' AND to_char(date,'MM') = %s AND to_char(date,'YYYY') = %s"
        )
        params = [month, year]
        if category:
            sql += " AND category = %s"
            params.append(category)
        sql += " ORDER BY amount DESC LIMIT %s"
        params.append(limit)
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        return [dict(r) for r in rows]

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

    # Categories
    def get_categories_by_type(self, type: str):
        cur = self._conn.cursor()
        cur.execute("SELECT id, name, icon FROM categories WHERE type = %s ORDER BY name", (type,))
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "name": r[1], "icon": r[2]} for r in rows]

    def list_all_categories(self):
        cur = self._conn.cursor()
        cur.execute("SELECT id, type, name, icon FROM categories ORDER BY type, name")
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "type": r[1], "name": r[2], "icon": r[3]} for r in rows]

    # Accounts
    def list_accounts(self):
        cur = self._conn.cursor()
        cur.execute("SELECT id, name, initial_balance, currency FROM accounts ORDER BY name")
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "name": r[1], "initial_balance": r[2], "currency": r[3]} for r in rows]

    def add_account(self, name: str, initial_balance: float = 0.0, currency: str = 'COP'):
        cur = self._conn.cursor()
        try:
            cur.execute("INSERT INTO accounts (name, initial_balance, currency) VALUES (%s, %s, %s) RETURNING id", (name, initial_balance, currency))
            aid = cur.fetchone()[0]
            cur.close()
            return aid
        except Exception:
            # exists
            cur.execute("SELECT id FROM accounts WHERE name = %s", (name,))
            r = cur.fetchone()
            cur.close()
            return r[0] if r else None

    def delete_account(self, account_id: int):
        cur = self._conn.cursor()
        cur.execute("DELETE FROM accounts WHERE id = %s", (account_id,))
        deleted = cur.rowcount > 0
        cur.close()
        return deleted

    def get_accounts_with_balances(self):
        cur = self._conn.cursor()
        sql = """
        SELECT a.name,
            a.initial_balance
            + COALESCE((SELECT SUM(CASE WHEN m.type='Ingreso' THEN m.amount WHEN m.type='Gasto' THEN -m.amount ELSE 0 END) FROM movements m WHERE m.account = a.name), 0)
            + COALESCE((SELECT SUM(t.amount) FROM transfers t WHERE t.to_account = a.name), 0)
            - COALESCE((SELECT SUM(t.amount) FROM transfers t WHERE t.from_account = a.name), 0) as balance,
        a.currency
        FROM accounts a ORDER BY a.name
        """
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return [{"name": r[0], "balance": r[1], "currency": r[2]} for r in rows]

    def get_movements_by_account(self, account: str):
        cur = self._conn.cursor()
        cur.execute("SELECT id, to_char(date,'YYYY-MM-DD') as date, type, amount, currency, fx_rate, category, description FROM movements WHERE account = %s ORDER BY date DESC", (account,))
        rows = cur.fetchall()
        cur.close()
        results = []
        for r in rows:
            results.append({
                'id': r[0], 'date': r[1], 'type': r[2], 'amount': r[3], 'currency': r[4], 'fx_rate': r[5], 'category': r[6], 'description': r[7]
            })
        return results

    def transfer_funds(self, from_account: str, to_account: str, amount: float, date: str, description: str = '', currency: str = 'COP'):
        cur = self._conn.cursor()
        # compute current balance similar to sqlite logic
        sql = """
        SELECT a.initial_balance
            + COALESCE((SELECT SUM(CASE WHEN m.type='Ingreso' THEN m.amount WHEN m.type='Gasto' THEN -m.amount ELSE 0 END) FROM movements m WHERE m.account = a.name), 0)
            + COALESCE((SELECT SUM(t.amount) FROM transfers t WHERE t.to_account = a.name), 0)
            - COALESCE((SELECT SUM(t.amount) FROM transfers t WHERE t.from_account = a.name), 0) as balance
        FROM accounts a WHERE a.name = %s
        """
        cur.execute(sql, (from_account,))
        row = cur.fetchone()
        current_balance = row[0] if row and row[0] is not None else 0.0
        if amount > current_balance:
            cur.close()
            raise ValueError('insufficient_funds')
        try:
            cur.execute("INSERT INTO transfers (date, from_account, to_account, amount, currency, description) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id", (date, from_account, to_account, amount, currency, description))
            tid = cur.fetchone()[0]
            cur.close()
            return tid
        except Exception:
            cur.close()
            raise

    def get_transfers_by_account(self, account: str):
        cur = self._conn.cursor()
        cur.execute("SELECT id, to_char(date,'YYYY-MM-DD') as date, from_account, to_account, amount, currency, description FROM transfers WHERE from_account = %s OR to_account = %s ORDER BY date DESC", (account, account))
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "date": r[1], "from": r[2], "to": r[3], "amount": r[4], "currency": r[5], "description": r[6]} for r in rows]

    def list_transfers(self):
        cur = self._conn.cursor()
        cur.execute("SELECT id, to_char(date,'YYYY-MM-DD') as date, from_account, to_account, amount, currency, description FROM transfers ORDER BY date DESC")
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "date": r[1], "from": r[2], "to": r[3], "amount": r[4], "currency": r[5], "description": r[6]} for r in rows]

    def delete_transfer(self, transfer_id: int):
        cur = self._conn.cursor()
        cur.execute("DELETE FROM transfers WHERE id = %s", (transfer_id,))
        deleted = cur.rowcount > 0
        cur.close()
        return deleted

    def update_transfer(self, transfer_id: int, **fields):
        allowed = {'date', 'from_account', 'to_account', 'amount', 'currency', 'description'}
        updates = []
        params = []
        for k, v in fields.items():
            if k in allowed:
                updates.append(f"{k} = %s")
                params.append(v)
        if not updates:
            return False
        params.append(transfer_id)
        sql = f"UPDATE transfers SET {', '.join(updates)} WHERE id = %s"
        cur = self._conn.cursor()
        cur.execute(sql, tuple(params))
        ok = cur.rowcount > 0
        cur.close()
        return ok

    def add_category(self, type: str, name: str, icon: str = None):
        cur = self._conn.cursor()
        try:
            cur.execute("INSERT INTO categories (type, name, icon) VALUES (%s, %s, %s) RETURNING id", (type, name, icon))
            cid = cur.fetchone()[0]
            cur.close()
            return cid
        except Exception:
            cur.execute("SELECT id FROM categories WHERE name = %s AND type = %s", (name, type))
            r = cur.fetchone()
            cur.close()
            return r[0] if r else None

    def add_denomination(self, value: float, label: str = None):
        cur = self._conn.cursor()
        try:
            cur.execute("INSERT INTO denominations (value, label) VALUES (%s, %s) RETURNING id", (value, label))
            did = cur.fetchone()[0]
            cur.close()
            return did
        except Exception:
            cur.execute("SELECT id FROM denominations WHERE value = %s", (value,))
            r = cur.fetchone()
            cur.close()
            return r[0] if r else None

    def list_denominations(self):
        cur = self._conn.cursor()
        cur.execute("SELECT id, value, label FROM denominations ORDER BY value DESC")
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "value": r[1], "label": r[2]} for r in rows]

    def delete_category(self, category_id: int):
        cur = self._conn.cursor()
        cur.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        ok = cur.rowcount > 0
        cur.close()
        return ok

    def delete_movement(self, movement_id: int):
        cur = self._conn.cursor()
        cur.execute("DELETE FROM movements WHERE id = %s", (movement_id,))
        ok = cur.rowcount > 0
        cur.close()
        return ok

    def update_movement(self, movement_id: int, **fields):
        allowed = {'date', 'type', 'amount', 'currency', 'fx_rate', 'category', 'description', 'account'}
        updates = []
        params = []
        for k, v in fields.items():
            if k in allowed:
                updates.append(f"{k} = %s")
                params.append(v)
        if not updates:
            return False
        params.append(movement_id)
        sql = f"UPDATE movements SET {', '.join(updates)} WHERE id = %s"
        cur = self._conn.cursor()
        cur.execute(sql, tuple(params))
        ok = cur.rowcount > 0
        cur.close()
        return ok

    def update_category(self, category_id: int, new_name: str):
        cur = self._conn.cursor()
        try:
            cur.execute("UPDATE categories SET name = %s WHERE id = %s", (new_name, category_id))
            ok = cur.rowcount > 0
            cur.close()
            return ok
        except Exception:
            cur.close()
            return False
