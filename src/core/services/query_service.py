from datetime import datetime
from ..domain.exceptions import InvalidDateFormatError


class MovementQueryService:
    def __init__(self, repository):
        self.repository = repository

    def _validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except Exception:
            raise InvalidDateFormatError("Formato de fecha incorrecto. Use AAAA-MM-DD")

    def find(self, date_from=None, date_to=None, category=None):
        if date_from:
            date_from = self._validate_date(date_from)
        if date_to:
            date_to = self._validate_date(date_to)
        if date_from and date_to and date_to < date_from:
            raise ValueError("La fecha 'to' no puede ser anterior a 'from'.")

        return self.repository.find_by_criteria(date_from=date_from, date_to=date_to, category=category)
