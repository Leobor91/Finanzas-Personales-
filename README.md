# Finanzas Personales - Registro de Movimientos

Implementación mínima para registrar movimientos (ingresos/gastos) usando SQLite, CLI y Flask.

Requisitos:
# Finanzas Personales

Pequeña aplicación de finanzas personales (CLI + UI en Flask) para registrar movimientos (ingresos/gastos), ejecutar consultas y generar reportes visuales. Está diseñada con arquitectura hexagonal para que las reglas de negocio sean probables y estén separadas del almacenamiento o la UI.

Inicio rápido
1. Crear un entorno virtual e instalar dependencias:
```bash
python -m pip install -r requirements.txt
```
2. Ejecutar la UI + API Flask:
```bash
python -m src.app
# Abrir http://127.0.0.1:5000/ui/reports
```
3. Usar el CLI (ejemplos):
```bash
python -m src.cli --date 2024-01-15 --type Ingreso --amount 100 --category Sueldo --description "Pago"
python -m src.cli list --from 2024-01-01 --to 2024-01-31
```

Estructura del proyecto (resumen)
- `src/core/domain` — entidades del dominio, excepciones y pequeños DTOs (la validación vive aquí).
- `src/core/ports` — interfaz del repositorio (`MovementRepositoryInterface`).
- `src/core/services` — servicios de aplicación (creación de movimientos, consultas, reportes).
- `src/infrastructure/database` — adaptador SQLite que implementa el repositorio y pequeñas migraciones.
- `src/templates` + `src/static` — plantillas Jinja y assets estáticos (Chart.js, CSS).
- `src/cli.py`, `src/app.py` — puntos de entrada (CLI y Flask UI/API).

Detalles importantes y convenciones
- Las validaciones de negocio deben vivir siempre en la entidad de dominio (`src/core/domain/entities.py`).
- Los mensajes de error en `src/core/domain/exceptions.py` son visibles para el usuario y están comprobados en tests: no los cambies sin actualizar tests.
- Instancia `SQLiteMovementRepository` (o cualquier conexión a la DB) en el mismo hilo/solicitud que la va a usar — no compartas objetos `sqlite3.Connection` entre hilos.
- `SQLiteMovementRepository` acepta `db_path` opcional para aislar la DB en tests (`tmp_path`).
- Las consultas SQL deben usar parámetros (no interpolación de strings). Sigue el patrón usado en `find_by_criteria()`.

Endpoints principales (selección)
- `POST /movements` — crear un movimiento (JSON: date, type, amount, category, description, currency, fx_rate).
- `GET /reports/balance?month=MM&year=YYYY` — totales mensuales + carryover.
- `GET /reports/categories?month=MM&year=YYYY` — totales por categoría para el periodo.
- `GET /reports/yearly?year=YYYY` — serie anual y totales.

Testing
- Ejecutar tests:
```bash
python -m pytest -q
```
- Para tests con DB aislada, usa `tmp_path` y construye `SQLiteMovementRepository(db_path=tmp_path/'test.db')`.

Extender el proyecto
- Para añadir campos a `Movement`: actualiza la entidad de dominio, la sentencia `CREATE TABLE` y las migraciones en el adaptador, los argumentos del CLI, el parsing en la API y los tests.
- Para agregar otro adaptador de persistencia: implementa la interfaz en `src/core/ports/repository.py` y úsalo desde los entrypoints.

Si quieres que añada CI (pytest + flake8), hooks pre-commit o ejemplos de tests para nuevas características, dímelo y preparo el parche.

