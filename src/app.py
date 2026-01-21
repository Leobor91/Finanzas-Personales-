from flask import Flask, request, jsonify
import sys
from pathlib import Path
from flask import render_template, redirect

# When executed as a script (python src/app.py) the package context is not set.
# Add project root to sys.path so absolute imports like `src.*` work.
if __package__ is None:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

from src.infrastructure.database.sqlite_adapter import SQLiteMovementRepository
from src.core.services.movement_service import MovementService
from src.core.domain.exceptions import InvalidAmountError, InvalidDateFormatError, InvalidTypeError

app = Flask(__name__, template_folder=str(Path(__file__).resolve().parent / 'templates'), static_folder=str(Path(__file__).resolve().parent / 'static'))


@app.route("/movements", methods=["POST"])
def create_movement():
    data = request.get_json() or {}
    repo = SQLiteMovementRepository()
    service = MovementService(repo)
    try:
        movement_id = service.create_movement(
            date=data.get("date"),
            type=data.get("type"),
            amount=data.get("amount"),
            category=data.get("category"),
            description=data.get("description"),
            currency=data.get("currency", 'COP'),
            fx_rate=data.get("fx_rate", None),
        )
        return jsonify({"id": movement_id}), 201
    except InvalidAmountError:
        return jsonify({"error": "El monto debe ser un valor numérico mayor a cero"}), 400
    except InvalidDateFormatError:
        return jsonify({"error": "Formato de fecha incorrecto. Use AAAA-MM-DD"}), 400
    except InvalidTypeError:
        return jsonify({"error": "Tipo debe ser 'Ingreso' o 'Gasto'"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass



@app.route("/movements", methods=["GET"])
def list_movements():
    # Support a single-day query via ?date=YYYY-MM-DD which maps to from==to
    date_param = request.args.get("date")
    if date_param:
        date_from = date_to = date_param
    else:
        date_from = request.args.get("from")
        date_to = request.args.get("to")
    category = request.args.get("category")
    repo = SQLiteMovementRepository()
    try:
        from src.core.services.query_service import MovementQueryService

        qs = MovementQueryService(repo)
        results = qs.find(date_from=date_from, date_to=date_to, category=category)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route("/reports/balance", methods=["GET"])
def report_balance():
    month = request.args.get("month")  # MM
    year = request.args.get("year")    # YYYY
    if not month or not year:
        return jsonify({"error": "Parámetros 'month' y 'year' son requeridos (MM, YYYY)."}), 400
    repo = SQLiteMovementRepository()
    try:
        from src.core.services.report_service import ReportService

        rs = ReportService(repo)
        # include previous month's net and cumulative net for the year
        bal = rs.monthly_with_carryover(month=month, year=year)
        return jsonify(bal), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route("/reports/categories", methods=["GET"])
def report_categories():
    month = request.args.get('month')
    year = request.args.get('year')
    repo = SQLiteMovementRepository()
    try:
        from src.core.services.report_service import ReportService

        rs = ReportService(repo)
        rows = rs.expenses_by_category(year=year, month=month)
        return jsonify([{"category": r.category, "total": r.total} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route("/reports/top-expenses", methods=["GET"])
def report_top_expenses():
    month = request.args.get("month")  # MM
    year = request.args.get("year")    # YYYY
    if not month or not year:
        return jsonify({"error": "Parámetros 'month' y 'year' son requeridos (MM, YYYY)."}), 400
    limit = int(request.args.get("limit", 5))
    category = request.args.get("category")
    repo = SQLiteMovementRepository()
    try:
        from src.core.services.report_service import ReportService

        rs = ReportService(repo)
        rows = rs.top_expenses(month=month, year=year, limit=limit, category=category)
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass

@app.route('/reports/years', methods=['GET'])
def report_years():
    repo = SQLiteMovementRepository()
    try:
        cur = repo.conn.cursor()
        cur.execute("SELECT DISTINCT strftime('%Y', date) as y FROM movements ORDER BY y DESC")
        rows = cur.fetchall()
        years = [r[0] for r in rows if r[0]]
        return jsonify(years), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route('/reports/yearly', methods=['GET'])
def report_yearly():
    year = request.args.get('year')
    if not year:
        return jsonify({'error': "Parámetro 'year' requerido (YYYY)."}), 400
    repo = SQLiteMovementRepository()
    try:
        from src.core.services.report_service import ReportService
        rs = ReportService(repo)
        summary = rs.yearly_summary(year)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route('/reports/daily', methods=['GET'])
def report_daily():
    month = request.args.get('month')
    year = request.args.get('year')
    if not month or not year:
        return jsonify({'error': "Parámetros 'month' (MM) y 'year' (YYYY) son requeridos."}), 400
    repo = SQLiteMovementRepository()
    try:
        rows = repo.get_daily_aggregates(month, year)
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route('/fx/latest', methods=['GET'])
def fx_latest():
    # Return latest exchange rates for COP to USD and EUR using exchangerate.host
    import urllib.request, json
    base = request.args.get('base', 'COP')
    symbols = request.args.get('symbols', 'USD,EUR')
    # First try exchangerate.host
    url1 = f'https://api.exchangerate.host/latest?base={base}&symbols={symbols}'
    try:
        with urllib.request.urlopen(url1, timeout=5) as resp:
            data = json.load(resp)
        # exchangerate.host may return {'success': False, 'error': {...}}
        if data.get('success', True) and 'rates' in data:
            return jsonify({'base': data.get('base', base), 'date': data.get('date'), 'rates': data.get('rates', {})}), 200
    except Exception:
        data = None

    # Fallback to open.er-api.com
    try:
        url2 = f'https://open.er-api.com/v6/latest/{base}'
        with urllib.request.urlopen(url2, timeout=5) as resp:
            data2 = json.load(resp)
        # data2 example: {'result':'success', 'rates': {'USD':0.00026, 'EUR':0.00024}, ...}
        rates2 = data2.get('rates', {})
        if rates2:
            # filter requested symbols
            wanted = {}
            for s in symbols.split(','):
                if s in rates2:
                    wanted[s] = rates2[s]
            return jsonify({'base': base, 'date': data2.get('time_last_update_utc') or data2.get('time_last_update_iso'), 'rates': wanted}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/categories', methods=['GET'])
def get_categories():
    type_q = request.args.get('type')
    if type_q not in ('Ingreso', 'Gasto'):
        return jsonify({'error': "Parámetro 'type' requerido y debe ser 'Ingreso' o 'Gasto'"}), 400
    repo = SQLiteMovementRepository()
    try:
        cats = repo.get_categories_by_type(type_q)
        return jsonify(cats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route('/categories', methods=['POST'])
def post_category():
    data = request.get_json() or {}
    type_q = data.get('type')
    name = data.get('name')
    icon = data.get('icon')
    if type_q not in ('Ingreso', 'Gasto') or not name:
        return jsonify({'error': "JSON debe contener 'type' ('Ingreso'|'Gasto') y 'name'"}), 400
    repo = SQLiteMovementRepository()
    try:
        cid = repo.add_category(type_q, name, icon)
        return jsonify({'id': cid, 'name': name, 'icon': icon}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route('/categories/all', methods=['GET'])
def get_all_categories():
    # If the client prefers HTML, redirect to the UI page so the browser shows the cards
    # Avoid redirecting AJAX/fetch requests (which often set X-Requested-With)
    is_ajax = request.headers.get('X-Requested-With','').lower() == 'xmlhttprequest'
    accept_hdr = request.headers.get('Accept','')
    if 'text/html' in accept_hdr and not is_ajax:
        return redirect('/ui/categories')

    repo = SQLiteMovementRepository()
    try:
        cats = repo.list_all_categories()
        return jsonify(cats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    repo = SQLiteMovementRepository()
    try:
        ok = repo.delete_category(cat_id)
        if ok:
            return jsonify({'deleted': True}), 200
        return jsonify({'deleted': False}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


@app.route('/categories/<int:cat_id>', methods=['PUT'])
def put_category(cat_id):
    data = request.get_json() or {}
    new_name = data.get('name')
    icon = data.get('icon')
    if not new_name:
        return jsonify({'error': "'name' requerido"}), 400
    repo = SQLiteMovementRepository()
    try:
        ok = repo.update_category(cat_id, new_name)
        # If icon provided, update separately
        if ok and icon is not None:
            cur = repo.conn.cursor()
            cur.execute("UPDATE categories SET icon = ? WHERE id = ?", (icon, cat_id))
            repo.conn.commit()
        if ok:
            return jsonify({'updated': True}), 200
        return jsonify({'updated': False}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        try:
            repo.close()
        except Exception:
            pass


from flask import render_template


@app.route("/")
def ui_index():
    return render_template('index.html')


@app.route("/ui/reports")
def ui_reports():
    return render_template('reports.html')


@app.route('/ui/categories')
def ui_categories():
    repo = SQLiteMovementRepository()
    try:
        cats = repo.list_all_categories()
        return render_template('categories.html', initial_categories=cats)
    finally:
        try:
            repo.close()
        except Exception:
            pass


if __name__ == "__main__":
    app.run(debug=True)
