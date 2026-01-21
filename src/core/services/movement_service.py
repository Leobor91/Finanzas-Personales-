from ..domain.entities import Movement


class MovementService:
    def __init__(self, repository):
        self.repository = repository

    def create_movement(self, date, type, amount, category, description=None, currency: str = 'COP', fx_rate: float | None = None):
        m = Movement(date=date, type=type, amount=amount, category=category, description=description, currency=currency, fx_rate=fx_rate)
        return self.repository.save(m)
