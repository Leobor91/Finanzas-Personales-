# Copilot instructions — Finanzas Personales (concise)

Short summary
- Language: Python 3.x. Package root: `src/`.
- App types: CLI (`src/cli.py`) and Flask UI/API (`src/app.py`, Jinja templates in `src/templates`).
- Persistence: SQLite DB `finance_app.db` managed by `SQLiteMovementRepository` (`src/infrastructure/database/sqlite_adapter.py`).

Big picture (why/what)
- Hexagonal architecture (ports & adapters):
  - Domain: `src/core/domain` (entities, exceptions, DTOs in `reports.py`).
  - Ports: `src/core/ports/repository.py` declares the repository interface.
  - Services: application logic in `src/core/services` (movement creation, queries, reports).
  - Infrastructure: SQLite adapter implements the port and includes small migrations (`_init_db()`).
  - Entry points: CLI and Flask create repository instances per invocation/request to avoid SQLite thread issues.

Key developer workflows
- Install deps:
  ```bash
  python -m pip install -r requirements.txt
  ```
- Run tests:
  ```bash
  python -m pytest -q
  ```
- Run app (UI + API):
  ```bash
  python -m src.app
  # UI at http://127.0.0.1:5000/ui/reports
  ```
- CLI examples:
  ```bash
  python -m src.cli --date 2024-01-15 --type Ingreso --amount 100 --category Sueldo --description "Pago"
  python -m src.cli list --from 2024-01-01 --to 2024-01-31
  python -m src.cli report balance --month 01 --year 2024
  ```

Project-specific conventions & gotchas
- Validation always lives in the domain entity (`src/core/domain/entities.py`) — keep business rules centralized.
- Error messages in `src/core/domain/exceptions.py` are user-visible and asserted in tests; do not change text without updating tests.
- Always instantiate `SQLiteMovementRepository` (or any DB connection) within the same thread/request that uses it — do not share `sqlite3.Connection` objects across threads.
- `SQLiteMovementRepository` accepts an optional `db_path` for test isolation; prefer passing `tmp_path` in tests.
- SQL must use parameterized queries. Follow `find_by_criteria()` and report methods for patterns (build SQL and params list incrementally).

Important code locations (quick links)
- Domain: `src/core/domain/entities.py`, `src/core/domain/exceptions.py`, `src/core/domain/reports.py`.
- Ports: `src/core/ports/repository.py`.
- Services: `src/core/services/movement_service.py`, `src/core/services/query_service.py`, `src/core/services/report_service.py`.
- Adapter: `src/infrastructure/database/sqlite_adapter.py` (CREATE TABLE, migrations, aggregate queries).
- API/UI: `src/app.py` (Flask routes) and `src/templates/reports.html` (frontend fetch + Chart.js logic).

API contracts to preserve
- `GET /reports/balance?month=MM&year=YYYY` → JSON with keys: `ingresos`, `gastos`, `neto`, `previous_net`, `cumulative_net`.
- `GET /reports/categories?month=MM&year=YYYY` → array of `{ category, total }` objects.
- `GET /reports/yearly?year=YYYY` → JSON: `{ months, ingresos, gastos, netos, total_ingresos, total_gastos, total_neto, expenses_by_category }`.

Testing guidance
- Use `tmp_path` fixture and construct `SQLiteMovementRepository(db_path=tmp_path / 'test.db')` for isolated DB tests.
- When changing domain validations, update unit tests that assert exact error messages.

Schema & migration notes
- `_init_db()` in `sqlite_adapter` runs lightweight migrations (ALTER TABLE ADD COLUMN) for `currency`, `fx_rate`, `icon` — keep this behavior when changing schema.

Frontend integration notes
- `src/templates/reports.html` expects numeric arrays and category lists; Chart.js rendering occurs client-side. The frontend applies currency conversion using per-movement `fx_rate` when present.

If you modify this file
- Preserve the exact CLI/API examples and the error message phrases shown in `exceptions.py`.

Questions to ask the maintainer
- Should newly added `Movement` fields be required or optional (current `currency` and `fx_rate` are optional)?
- Any preferred FX provider or requirement to persist FX source/timestamp with movements?

If you want CI (pytest run + flake8) or pre-commit hooks added, tell me which one and I will add a focused patch.
# Copilot instructions for Finanzas Personales repository

This repository implements a minimal Hexagonal-architecture Python app to register and query financial movements (ingresos/gastos). Use these notes to help an AI coding agent become productive quickly and avoid common mistakes.

Quick summary
- Language: Python 3.x. Package root is `src/`.
- App types: CLI (`src/cli.py`) and Flask API (`src/app.py`).
- Persistence: SQLite file `finance_app.db` created lazily by `SQLiteMovementRepository` (in `src/infrastructure/database/sqlite_adapter.py`).

Big-picture architecture
- Hexagonal (Ports & Adapters):
  - Core domain: `src/core/domain` (`entities.py`, `exceptions.py`, `reports.py`).
  - Ports: `src/core/ports/repository.py` defines `MovementRepositoryInterface` (save, find_by_criteria, aggregates).
  - Services: application logic in `src/core/services` (`movement_service.py`, `query_service.py`, `report_service.py`).
  - Infrastructure: SQLite adapter in `src/infrastructure/database/sqlite_adapter.py` implements repository methods and initializes DB/table.
  - Entry adapters: CLI (`src/cli.py`) and Flask (`src/app.py`) create repository instances per request to avoid SQLite threading issues.

Why this structure matters
- Validation belongs in the domain entity (`Movement`) not in adapters — keep business rules centralized.
- Repositories accept optional `db_path` for testability (use `tmp_path` in tests).
- The Flask app creates a new `SQLiteMovementRepository` per HTTP request to avoid "SQLite objects created in a thread" errors.

Critical developer workflows
- Install dependencies:
  ```bash
  python -m pip install -r requirements.txt
  ```
- Run tests (recommended to run from project root):
  ```bash
  python -m pytest -q
  ```
- CLI examples:
  - Add movement:
    ```bash
    python -m src.cli --date 2024-01-15 --type Ingreso --amount 100 --category Sueldo --description "Pago"
    ```
  - List movements (filters):
    ```bash
    python -m src.cli list --from 2024-01-01 --to 2024-01-31 --category Super
    ```
  - Reports (CLI):
    ```bash
    python -m src.cli report balance --month 01 --year 2024
    python -m src.cli report categories
    ```
- Run Flask API (preferred as module):
  ```bash
  python -m src.app
  # GET /movements?from=2024-01-01&to=2024-01-31&category=Super
  # GET /reports/balance?month=01&year=2024
  # GET /reports/categories
  ```

Project-specific conventions & patterns
- Use relative imports inside `src/` only when referencing sibling modules; prefer absolute `src.*` imports in top-level modules. The project contains a `sys.path` fallback in `src/app.py` to allow `python src/app.py`, but the recommended pattern is `python -m src.app`.
- Domain validations are strict and message-sensitive. The CLI and Flask endpoints expect the exact error messages defined in `src/core/domain/exceptions.py`.
- Repositories should: initialize DB with `CREATE TABLE IF NOT EXISTS`, expose a `close()` method, and accept an optional `db_path` for tests.
- SQL is built with parameterized queries (avoid string interpolation) — follow existing `find_by_criteria` and report methods as examples.

Integration points and external dependencies
- SQLite: standard library `sqlite3` (DB file `finance_app.db` in CWD by default).
- Flask: provides API endpoints; see `src/app.py`.
- Tests use `pytest` and `tmp_path` for ephemeral DB files.
- Optional: CLI rendering libraries (e.g., `tabulate`, `plotille`) are not required; avoid adding deps unless necessary.

Notes on threading and process model
- Always create DB connections in the thread that will use them. The codebase avoids sharing a `sqlite3.Connection` across threads by instantiating `SQLiteMovementRepository` inside each request handler or command execution.

Files to inspect for common tasks
- Add new persistence logic: `src/infrastructure/database/sqlite_adapter.py` and `src/core/ports/repository.py`.
- Add business rules: `src/core/domain/entities.py` and `src/core/domain/exceptions.py` (preserve error messages).
- Add queries/reports: `src/core/services/query_service.py`, `src/core/services/report_service.py` and the new DTOs in `src/core/domain/reports.py`.
- Add CLI behavior: `src/cli.py` (dispatches `list` and `report` subcommands).

Examples (copy-paste safe snippets)
- Parameterized SELECT with optional filters (pattern used in SQLite adapter):
  ```python
  sql = "SELECT ... FROM movements WHERE 1=1"
  params = []
  if date_from:
      sql += " AND date >= ?"
      params.append(date_from)
  # ...
  cur.execute(sql, params)
  ```

- Aggregate query for monthly balance:
  ```sql
  SELECT type, SUM(amount) as total
  FROM movements
  WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
  GROUP BY type
  ```

Testing notes
- Use `tmp_path` to create isolated DB files and pass them to `SQLiteMovementRepository(db_path=tmp_path / 'test.db')`.
- Tests already cover domain validation, repository integration and basic reports. When changing error strings in exceptions, update tests accordingly.

If you change this file
- Preserve example commands and error message phrases.
- Update `README.md` and tests when adding/removing CLI flags or changing API contract.

Questions to ask when unsure
- Should new fields be required in the `Movement` domain or optional?
- Should reports be paginated or only full aggregates?
- Which CLI/HTTP interfaces must remain backward-compatible?

If anything is unclear or you'd like specific additions (CI workflow, pre-commit hooks, or richer CLI output), say which one and I will add it.
# Copilot instructions for Finanzas Personales repository

This project implements a minimal Hexagonal-architecture app for registering financial movements (ingresos/gastos) with a CLI and optional Flask API. These instructions help AI coding agents become productive quickly by highlighting project structure, conventions, workflows and concrete examples.

Key points (quick reference)
- Language: Python 3.x. Use the repository `src/` package as the import root (run modules with `python -m src.<module>` when using the CLI).
- Persistence: SQLite file `finance_app.db` created automatically in the current working directory by `SQLiteMovementRepository`.
- Architecture: Hexagonal (core domain, ports, services, infrastructure adapters, entry adapters). See `src/core/` and `src/infrastructure/`.

Important files and intents
- `src/core/domain/entities.py` — Domain entity `Movement` and strict validations:
  - Date must be `YYYY-MM-DD` (raises `InvalidDateFormatError`).
  - Amount must be numeric and > 0 (raises `InvalidAmountError`) — exact error message expected by CLI/API.
  - Type must be `Ingreso` or `Gasto` (raises `InvalidTypeError`).
- `src/core/domain/exceptions.py` — Business exceptions used by CLI and Flask to map to user-facing messages.
- `src/core/ports/repository.py` — Port (abstract interface) `MovementRepositoryInterface` with `save(movement)`.
- `src/core/services/movement_service.py` — Application service that instantiates a `Movement` and delegates persistence to a repository.
- `src/infrastructure/database/sqlite_adapter.py` — SQLite adapter implementing the repository port and creating the DB/table via `CREATE TABLE IF NOT EXISTS`.
- `src/cli.py` — CLI entrypoint (argparse). Run as `python -m src.cli ...`. CLI expects the exact error messages for validation failures.
- `src/app.py` — Minimal Flask app exposing `POST /movements`. Returns 400 with JSON error messages matching domain exceptions.

Project-specific conventions and patterns
- Package imports use relative imports inside `src/` (e.g. `from .core.services import ...` when at package top-level). When running as a module, run from project root with `python -m src.cli` or `python src/app.py`.
- All user-visible error messages are declared in domain exceptions and consumed upstream (CLI/Flask) — preserve phrasing when writing tests or error handling so tests/assertions remain stable.
- DB file path: `Path.cwd() / "finance_app.db"` in the adapter. Tests use `SQLiteMovementRepository(db_path=...)` with a temporary path — prefer dependency-injecting `db_path` when writing tests or scripts.
- Use the port interface `MovementRepositoryInterface` when implementing alternative storage (mock, in-memory, or other databases).

Developer workflows (commands)
- Install deps:
  ```bash
  python -m pip install -r requirements.txt
  ```
- Run unit + integration tests:
  ```bash
  python -m pytest -q
  ```
- Run CLI example:
  ```bash
  python -m src.cli --date 2024-01-15 --type Ingreso --amount 100 --category Sueldo --description "Pago"
  ```
- Run Flask API locally:
  ```bash
  python src/app.py
  # then POST JSON to http://127.0.0.1:5000/movements
  ```

Patterns & examples to follow when contributing code
- Validation location: keep business validation in `src/core/domain/entities.py` so services and adapters remain slim. Do not duplicate validation logic in adapters.
- Repository interface: new adapters should implement `save(movement)` and accept an optional `db_path` or connection injection for testability.
- Tests: current tests use `pytest` and place unit tests under `tests/unit` and integration tests under `tests/integration`. Use `tmp_path` fixtures for DB files in integration tests.
- CLI vs API behavior: CLI prints plain text messages; API returns JSON with `error` keys and HTTP 400 for validation errors. Keep messages consistent between interfaces.

Integration & extension notes
- If adding new fields to `Movement`, update:
  - `src/core/domain/entities.py` (validation + constructor signature)
  - `CREATE_TABLE_SQL` in `src/infrastructure/database/sqlite_adapter.py`
  - CLI arguments in `src/cli.py` and JSON parsing in `src/app.py`
  - Tests under `tests/unit` and `tests/integration`
- To change DB location from `Path.cwd()`, modify `DB_FILENAME` or inject `db_path` when constructing `SQLiteMovementRepository`.

What not to change without tests
- Do not change the exact text of validation error messages in `exceptions.py` without updating tests and CLI/API message checks.
- Do not alter the `type` CHECK constraint in SQL without updating validation rules and tests.

If something is unclear
- Ask: "Should new fields be required in the domain model or optional?" or "Which interfaces must remain backward-compatible (CLI, API)?"

Revision guidance
- If updating this file, preserve the examples and command snippets. Keep the instructions terse and focused on repository-specific facts.
