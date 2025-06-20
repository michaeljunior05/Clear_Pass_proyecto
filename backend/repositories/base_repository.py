# backend/repositories/base_repository.py
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    """
    Clase abstracta base para todos los repositorios en el sistema.
    Define una interfaz común (contrato) para las operaciones CRUD básicas
    que cualquier repositorio debe implementar.
    """

    @abstractmethod
    def get_all_users(self):
        """
        Método abstracto para obtener todas las entidades gestionadas por el repositorio.
        Puede aceptar argumentos adicionales para filtros, paginación, etc.
        Debe ser implementado por las subclases concretas.
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        """
        Método abstracto para obtener una entidad específica por su identificador único.
        Debe ser implementado por las subclases concretas.
        """
        pass

