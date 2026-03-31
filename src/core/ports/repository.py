from abc import ABC, abstractmethod


class MovementRepositoryInterface(ABC):
    @abstractmethod
    def save(self, movement):
        """Persiste un Movement y devuelve el id (int)."""
        raise NotImplementedError

    @abstractmethod
    def find_by_criteria(self, date_from=None, date_to=None, category=None, type_=None, user_id: int | None = None):
        """Devuelve una lista de movimientos que cumplan los criterios (opcionalmente).
        Los parámetros son cadenas: date_from YYYY-MM-DD, date_to YYYY-MM-DD, category para búsqueda parcial.
        Cuando `user_id` se pasa, debe filtrar solo los movimientos del usuario.
        """
        raise NotImplementedError

    @abstractmethod
    def get_monthly_aggregates(self, month: str, year: str, user_id: int | None = None):
        """Devuelve agregados por tipo para un mes y año dados. month debe ser 'MM', year 'YYYY'.
        Si `user_id` se pasa, filtrar solo movimientos del usuario."""
        raise NotImplementedError

    @abstractmethod
    def get_expenses_by_category(self, year: str = None, month: str = None, user_id: int | None = None):
        """Devuelve la suma de gastos agrupada por categoría, ordenada por monto descendente.
        Si `year`/`month` se pasan, filtrar por fecha. Si `user_id` se pasa, filtrar por usuario."""
        raise NotImplementedError

    @abstractmethod
    def get_top_expenses(self, month: str, year: str, limit: int = 5, category: str = None, user_id: int | None = None):
        """Devuelve las filas de los mayores gastos para un mes y año dados.

        Debe retornar una lista de diccionarios con: category, description, amount, date
        """
        raise NotImplementedError

    @abstractmethod
    def get_categories_by_type(self, type: str, user_id: int | None = None):
        """Devuelve una lista de categorías para un tipo dado ('Ingreso'|'Gasto').
        Cuando `user_id` es provisto, debe incluir categorías globales (user_id NULL)
        y las pertenecientes al usuario. Cada categoría incluye `id`, `name` y opcionalmente `icon`.
        """
        raise NotImplementedError

    @abstractmethod
    def add_category(self, type: str, name: str, icon: str = None, user_id: int | None = None):
        """Añade una categoría nueva al repositorio y devuelve su id o nombre.
        `icon` es opcional (emoji o URL).
        """
        raise NotImplementedError

    @abstractmethod
    def list_all_categories(self, user_id: int | None = None):
        """Devuelve todas las categorías con id, type, name y opcionalmente icon.
        Si `user_id` se pasa, debe devolver solo categorías del usuario (y/o globales según la implementación)."""
        raise NotImplementedError

    @abstractmethod
    def delete_category(self, category_id: int):
        """Elimina una categoría por id. Devuelve True si se eliminó."""
        raise NotImplementedError

    @abstractmethod
    def update_category(self, category_id: int, new_name: str, icon: str = None):
        """Actualiza el nombre (y opcionalmente icon) de una categoría. Devuelve True si se actualizó."""
        raise NotImplementedError

    @abstractmethod
    def get_yearly_aggregates(self, year: str, user_id: int | None = None):
        """Devuelve totales por mes para el año dado.
        Retorna un dict con claves 'MM' -> {'Ingreso': total, 'Gasto': total}.
        Si `user_id` se pasa, filtrar por usuario."""
        raise NotImplementedError

    @abstractmethod
    def get_daily_aggregates(self, month: str, year: str, user_id: int | None = None):
        """Devuelve totales por día para el mes y año dados.
        Retorna un dict con claves '01'..'31' -> {'Ingreso': total, 'Gasto': total}.
        Si `user_id` se pasa, filtrar por usuario."""
        raise NotImplementedError
