from dataclasses import dataclass


@dataclass
class MonthlyBalance:
    month: str  # 'MM'
    year: str   # 'YYYY'
    total_ingresos: float = 0.0
    total_gastos: float = 0.0


@dataclass
class CategorySummary:
    category: str
    total: float
