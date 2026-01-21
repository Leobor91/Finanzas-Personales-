import pytest
from src.core.domain.entities import Movement
from src.core.domain.exceptions import InvalidAmountError, InvalidDateFormatError, InvalidTypeError


def test_movement_valid():
    m = Movement(date="2024-01-15", type="Ingreso", amount=100, category="Sueldo", description="Pago")
    assert m.amount == 100.0
    assert m.date == "2024-01-15"


def test_movement_invalid_amount_zero():
    with pytest.raises(InvalidAmountError):
        Movement(date="2024-01-15", type="Ingreso", amount=0, category="Sueldo")


def test_movement_negative_amount():
    with pytest.raises(InvalidAmountError):
        Movement(date="2024-01-15", type="Ingreso", amount=-5, category="Sueldo")


def test_movement_invalid_date_format():
    with pytest.raises(InvalidDateFormatError):
        Movement(date="15/01/2024", type="Ingreso", amount=10, category="Otros")


def test_movement_invalid_type():
    with pytest.raises(InvalidTypeError):
        Movement(date="2024-01-15", type="Transferencia", amount=10, category="Otros")
