import argparse
from .infrastructure.database.sqlite_adapter import SQLiteMovementRepository
from .core.services.movement_service import MovementService
from .core.domain.exceptions import InvalidAmountError, InvalidDateFormatError, InvalidTypeError


def build_parser():
    p = argparse.ArgumentParser(prog="finance", description="Registro de movimientos financieros")
    p.add_argument("--date", required=True, help="Fecha AAAA-MM-DD")
    p.add_argument("--type", required=True, choices=["Ingreso", "Gasto"], help="Tipo: Ingreso o Gasto")
    p.add_argument("--amount", required=True, help="Monto (numérico, > 0)")
    p.add_argument("--category", required=True, help="Categoría (texto libre)")
    p.add_argument("--description", default="", help="Descripción (opcional)")
    p.add_argument("--currency", default="COP", help="Moneda (COP, USD, EUR)")
    p.add_argument("--fx-rate", dest="fx_rate", type=float, help="Tasa FX (COP por 1 unidad de moneda seleccionada). Opcional")
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    repo = SQLiteMovementRepository()
    service = MovementService(repo)
    try:
        movement_id = service.create_movement(
            date=args.date,
            type=args.type,
            amount=args.amount,
            category=args.category,
            description=args.description or None,
            currency=args.currency or 'COP',
            fx_rate=args.fx_rate,
        )
        print(f"Movimiento registrado con id: {movement_id}")
    except InvalidAmountError:
        print("El monto debe ser un valor numérico mayor a cero")
        return 1
    except InvalidDateFormatError:
        print("Formato de fecha incorrecto. Use AAAA-MM-DD")
        return 1
    except InvalidTypeError:
        print("Tipo debe ser 'Ingreso' o 'Gasto'")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 2
    finally:
        repo.close()


if __name__ == "__main__":
    import sys

    # Simple dispatch: if first arg is 'list' call the list handler, otherwise call main (add)
    argv = sys.argv[1:]
    if len(argv) > 0 and argv[0] == "list":
        # call list_main with remaining args
        raise SystemExit(list_main(argv[1:]))
    if len(argv) > 0 and argv[0] == "report":
        # report subcommands: balance | categories
        if len(argv) >= 2 and argv[1] == "balance":
            # args after 'report balance'
            # expected: --month MM --year YYYY
            import argparse as _arg

            p = _arg.ArgumentParser(prog="finance report balance")
            p.add_argument("--month", required=True)
            p.add_argument("--year", required=True)
            args2 = p.parse_args(argv[2:])
            repo = SQLiteMovementRepository()
            try:
                from .core.services.report_service import ReportService

                rs = ReportService(repo)
                bal = rs.monthly_with_carryover(month=args2.month, year=args2.year)
                print(f"Mes: {bal['month']}/{bal['year']}  Ingresos: {bal['ingresos']:.2f}  Gastos: {bal['gastos']:.2f}  Neto: {bal['neto']:.2f}  MesAnteriorNeto: {bal['previous_net']:.2f}  Acumulado: {bal['cumulative_net']:.2f}")
            finally:
                repo.close()
            raise SystemExit(0)
        if len(argv) >= 2 and argv[1] == "categories":
            repo = SQLiteMovementRepository()
            try:
                from .core.services.report_service import ReportService

                rs = ReportService(repo)
                rows = rs.expenses_by_category()
                if not rows:
                    print("No se encontraron categorías con gastos")
                    raise SystemExit(0)
                print(f"{'CATEGORY':20}  {'TOTAL':>10}")
                for r in rows:
                    print(f"{r.category:20}  {r.total:10.2f}")
            finally:
                repo.close()
            raise SystemExit(0)
    else:
        raise SystemExit(main(argv))








def build_list_parser():
    p = argparse.ArgumentParser(prog="finance list", description="Listar movimientos")
    p.add_argument("--from", dest="date_from", help="Fecha desde AAAA-MM-DD")
    p.add_argument("--to", dest="date_to", help="Fecha hasta AAAA-MM-DD")
    p.add_argument("--category", dest="category", help="Filtro por categoría (coincidencia parcial)")
    return p


def list_main(argv=None):
    parser = build_list_parser()
    args = parser.parse_args(argv)
    repo = SQLiteMovementRepository()
    try:
        from .core.services.query_service import MovementQueryService

        qs = MovementQueryService(repo)
        results = qs.find(date_from=args.date_from, date_to=args.date_to, category=args.category)
        if not results:
            print("No se encontraron movimientos para los criterios seleccionados")
            return 0
        # simple table
        print(f"{'ID':>3}  {'DATE':10}  {'TYPE':7}  {'AMOUNT':8}  {'CATEGORY':15}  DESCRIPTION")
        for r in results:
            print(f"{r['id']:>3}  {r['date']:10}  {r['type']:7}  {r['amount']:8.2f}  {r['category'][:15]:15}  {r.get('description','')}")
        return 0
    finally:
        repo.close()

