from ..domain.entities import Movement


class MovementService:
    def __init__(self, repository):
        self.repository = repository

    def create_movement(self, date, type, amount, category, description=None, currency: str = 'COP', fx_rate: float | None = None, account: str | None = None, user_id: int | None = None):
        m = Movement(date=date, type=type, amount=amount, category=category, description=description, currency=currency, fx_rate=fx_rate, account=account, user_id=user_id)
        return self.repository.save(m, user_id=user_id)
