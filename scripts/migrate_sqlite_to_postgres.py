"""Migrate data from the local SQLite `finance_app.db` to Postgres pointed by `DATABASE_URL`.

Usage:
  Set `DATABASE_URL` env var (postgres://...) and run:
    python scripts/migrate_sqlite_to_postgres.py

This script inserts rows that do not already exist in Postgres. It will NOT delete or overwrite existing data.
"""
import os
import sqlite3
import psycopg2

SQLITE_DB = os.environ.get('SQLITE_DB') or 'finance_app.db'
PG_URL = os.environ.get('DATABASE_URL')
MIGRATION_SCHEMA = os.environ.get('MIGRATION_SCHEMA')

if not PG_URL:
    print('Please set DATABASE_URL env var pointing to your Postgres instance.')
    raise SystemExit(1)


def table_exists_sqlite(conn, name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    r = cur.fetchone()
    cur.close()
    return r is not None


def migrate():
    sconn = sqlite3.connect(SQLITE_DB)
    scol = sconn.cursor()

    pconn = psycopg2.connect(PG_URL)
    pcur = pconn.cursor()

    # If a target schema is provided, set the session search_path so DDL/INSERT operate in that schema
    if MIGRATION_SCHEMA:
        try:
            pcur.execute(f"CREATE SCHEMA IF NOT EXISTS {MIGRATION_SCHEMA}")
        except Exception:
            pass
        pcur.execute(f"SET search_path TO {MIGRATION_SCHEMA}, public")

    # Ensure target tables exist in Postgres (will be created in current search_path/schema)
    DDL = '''
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
    '''
    try:
        pcur.execute(DDL)
    except Exception:
        # If DDL fails, continue; inserts may still work if tables created elsewhere
        pass

    print('Migrating categories...')
    if table_exists_sqlite(sconn, 'categories'):
        scol.execute('SELECT type, name, icon FROM categories')
        for typ, name, icon in scol.fetchall():
            try:
                pcur.execute("INSERT INTO categories (type, name, icon) VALUES (%s,%s,%s) ON CONFLICT (type,name) DO NOTHING", (typ, name, icon))
            except Exception as e:
                print('category insert error', e)
    else:
        print('  no categories table in sqlite; skipping')

    print('Migrating accounts...')
    if table_exists_sqlite(sconn, 'accounts'):
        scol.execute('SELECT name, initial_balance, currency FROM accounts')
        for name, initial, currency in scol.fetchall():
            try:
                pcur.execute("INSERT INTO accounts (name, initial_balance, currency) VALUES (%s,%s,%s) ON CONFLICT (name) DO NOTHING", (name, initial, currency))
            except Exception as e:
                print('account insert error', e)
    else:
        print('  no accounts table in sqlite; skipping')

    print('Migrating denominations...')
    if table_exists_sqlite(sconn, 'denominations'):
        scol.execute('SELECT value, label FROM denominations')
        for value, label in scol.fetchall():
            try:
                pcur.execute("INSERT INTO denominations (value, label) VALUES (%s,%s) ON CONFLICT (value) DO NOTHING", (value, label))
            except Exception as e:
                print('denomination insert error', e)
    else:
        print('  no denominations table in sqlite; skipping')

    print('Migrating transfers...')
    if table_exists_sqlite(sconn, 'transfers'):
        scol.execute('SELECT date, from_account, to_account, amount, currency, description FROM transfers')
        for date, f, t, amount, currency, desc in scol.fetchall():
            try:
                # avoid duplicate transfers by simple match
                pcur.execute("SELECT id FROM transfers WHERE date = %s AND from_account = %s AND to_account = %s AND amount = %s AND COALESCE(description,'') = COALESCE(%s,'')", (date, f, t, amount, desc))
                if not pcur.fetchone():
                    pcur.execute("INSERT INTO transfers (date, from_account, to_account, amount, currency, description) VALUES (%s,%s,%s,%s,%s,%s)", (date, f, t, amount, currency, desc))
            except Exception as e:
                print('transfer insert error', e)
    else:
        print('  no transfers table in sqlite; skipping')

    print('Migrating categories done.')

    print('Migrating movements...')
    count = 0
    if table_exists_sqlite(sconn, 'movements'):
        # Inspect available columns in the sqlite movements table and select only existing ones
        scol.execute("PRAGMA table_info(movements)")
        existing_cols = [r[1] for r in scol.fetchall()]
        desired = ['date', 'type', 'amount', 'currency', 'fx_rate', 'category', 'description', 'account']
        select_cols = [c for c in desired if c in existing_cols]
        if not select_cols:
            print('  movements table exists but has no expected columns; skipping')
        else:
            scol.execute(f"SELECT {', '.join(select_cols)} FROM movements")
            for row in scol.fetchall():
                # map row values to a dict filling missing desired cols with None
                vals = {col: None for col in desired}
                for i, col in enumerate(select_cols):
                    vals[col] = row[i]
                date = vals['date']
                typ = vals['type']
                amount = vals['amount']
                currency = vals['currency']
                fx_rate = vals['fx_rate']
                category = vals['category']
                desc = vals['description']
                account = vals['account']
                try:
                    pcur.execute(
                        "SELECT id FROM movements WHERE date = %s AND type = %s AND amount = %s AND COALESCE(category,'') = COALESCE(%s,'') AND COALESCE(description,'') = COALESCE(%s,'') AND COALESCE(account,'') = COALESCE(%s,'')",
                        (date, typ, amount, category, desc, account),
                    )
                    if not pcur.fetchone():
                        pcur.execute(
                            "INSERT INTO movements (date, type, amount, currency, fx_rate, category, description, account) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                            (date, typ, amount, currency or 'COP', fx_rate, category, desc, account),
                        )
                        count += 1
                except Exception as e:
                    print('movement insert error', e)
    else:
        print('  no movements table in sqlite; skipping')

    print(f'Inserted {count} new movements.')

    pconn.commit()
    pcur.close()
    pconn.close()
    scol.close()
    sconn.close()

    print('Migration complete. Review Postgres DB for results.')


if __name__ == '__main__':
    migrate()
