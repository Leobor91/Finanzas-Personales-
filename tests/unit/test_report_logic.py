from src.core.services.report_service import ReportService


class DummyRepo:
    def get_monthly_aggregates(self, month, year):
        if month == "01" and year == "2024":
            return {"Ingreso": 200.0, "Gasto": 50.0}
        return {}

    def get_expenses_by_category(self):
        return [{"category": "Super", "total": 120.0}, {"category": "Transporte", "total": 30.0}]


def test_monthly_balance():
    repo = DummyRepo()
    rs = ReportService(repo)
    bal = rs.monthly_balance("01", "2024")
    assert bal.total_ingresos == 200.0
    assert bal.total_gastos == 50.0


def test_expenses_by_category():
    repo = DummyRepo()
    rs = ReportService(repo)
    rows = rs.expenses_by_category()
    assert len(rows) == 2
    assert rows[0].category == "Super"
    assert rows[0].total == 120.0
