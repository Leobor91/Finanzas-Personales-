# Finanzas Personales - Registro de Movimientos

Implementación mínima para registrar movimientos (ingresos/gastos) usando SQLite, CLI y Flask.

Requisitos:
- Python 3.x
- Instalar dependencias: `pip install -r requirements.txt`

Uso CLI:

```bash
python -m src.cli --date 2024-01-15 --type Ingreso --amount 100 --category Sueldo --description "Pago"
```

Uso Flask:

Recomendado (ejecutar como módulo para asegurar imports de paquete):

```bash
python -m src.app
# POST JSON a http://127.0.0.1:5000/movements
```

Alternativa (ejecutar como script):

```bash
python src/app.py
# El proyecto añade temporalmente el directorio raíz al `sys.path` para permitir esta forma.
```

La base de datos `finance_app.db` se crea automáticamente en el directorio de trabajo.
