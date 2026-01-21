from src.infrastructure.database.sqlite_adapter import SQLiteMovementRepository
from src.core.domain.entities import Movement


def test_find_by_date_range_and_category(tmp_path):
    db_file = tmp_path / "test_q.db"
    repo = SQLiteMovementRepository(db_path=db_file)
    # insert sample data
    m1 = Movement(date="2024-01-10", type="Ingreso", amount=100, category="Sueldo", description="Pago")
    m2 = Movement(date="2024-01-15", type="Gasto", amount=20, category="Supermercado", description="Compra")
    m3 = Movement(date="2024-02-01", type="Gasto", amount=50, category="Super", description="Compra2")
    repo.save(m1)
    repo.save(m2)
    repo.save(m3)

    # full range
    res = repo.find_by_criteria(date_from="2024-01-01", date_to="2024-01-31")
    assert any(r["date"] == "2024-01-15" for r in res)

    # category partial
    res2 = repo.find_by_criteria(category="Super")
    assert len(res2) == 2

    repo.close()
