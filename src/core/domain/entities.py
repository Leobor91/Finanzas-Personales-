from datetime import datetime
from .exceptions import InvalidAmountError, InvalidDateFormatError, InvalidTypeError


class Movement:
    def __init__(self, date: str, type: str, amount, category: str, description: str | None = None, currency: str = 'COP', fx_rate: float | None = None):
        # Fecha: YYYY-MM-DD
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            raise InvalidDateFormatError("Formato de fecha incorrecto. Use AAAA-MM-DD")

        # Monto: numérico > 0
        try:
            value = float(amount)
        except Exception:
            raise InvalidAmountError("El monto debe ser un valor numérico mayor a cero")
        if value <= 0:
            raise InvalidAmountError("El monto debe ser un valor numérico mayor a cero")

        # Tipo: Ingreso/Gasto
        if type not in ("Ingreso", "Gasto"):
            raise InvalidTypeError("Tipo debe ser 'Ingreso' o 'Gasto'")

        self.date = date
        self.type = type
        self.amount = value
        self.category = category
        self.description = description
        # Currency and FX rate (optional). Stored as provided; default currency is COP
        self.currency = currency or 'COP'
        self.fx_rate = float(fx_rate) if fx_rate is not None else None
