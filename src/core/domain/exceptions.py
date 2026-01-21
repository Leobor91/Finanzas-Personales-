class InvalidAmountError(ValueError):
    """El monto debe ser un valor numérico mayor a cero"""
    pass


class InvalidDateFormatError(ValueError):
    """Formato de fecha incorrecto. Use AAAA-MM-DD"""
    pass


class InvalidTypeError(ValueError):
    """Tipo inválido. Debe ser 'Ingreso' o 'Gasto'"""
    pass
