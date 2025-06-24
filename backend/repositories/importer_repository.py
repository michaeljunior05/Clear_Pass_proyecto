# backend/repositories/importer_repository.py
import logging
from typing import List, Optional
import uuid # Asegúrate de importar uuid si lo usas para generar IDs aquí

from backend.repositories.json_storage import JSONStorage # Importa JSONStorage
from backend.models.importer import Importer

logger = logging.getLogger(__name__)

# NOTA IMPORTANTE: Esta clase ya NO hereda de BaseRepository
class ImporterRepository:
    """
    Gestiona la persistencia de objetos Importer utilizando JSONStorage.
    """
    def __init__(self, storage: JSONStorage):
        """
        Inicializa ImporterRepository.

        Args:
            storage (JSONStorage): Una instancia de JSONStorage para el acceso a datos.
        """
        # No se llama a super().__init__() porque no hereda de BaseRepository.
        self.storage = storage
        self.entity_type = "importers" # Define la clave bajo la cual se guardarán los importadores en el JSON
        logger.info("ImporterRepository inicializado.")

    def add_importer(self, importer: Importer) -> Optional[Importer]:
        """
        Añade un nuevo importador al almacenamiento.
        
        Args:
            importer (Importer): El objeto Importer a añadir.
        Returns:
            Importer | None: El objeto Importer guardado con su ID, o None si falla.
        """
        # JSONStorage.save_entity generará el ID si importer.id es None o vacío.
        importer_data = importer.to_dict()
        try:
            saved_data = self.storage.save_entity(entity_type=self.entity_type, item_data=importer_data)
            if saved_data:
                logger.info(f"Importador con ID {saved_data.get('id')} guardado exitosamente.")
                return Importer.from_dict(saved_data)
            return None
        except Exception as e:
            logger.error(f"Error al guardar importador: {e}")
            return None

    def get_importer_by_id(self, importer_id: str) -> Optional[Importer]:
        """
        Busca un importador por su ID.
        
        Args:
            importer_id (str): El ID del importador a buscar.
        Returns:
            Importer | None: El objeto Importer si se encuentra, o None si no.
        """
        importer_data = self.storage.get_by_id(entity_type=self.entity_type, item_id=importer_id)
        if importer_data:
            return Importer.from_dict(importer_data)
        return None

    def get_all_importers(self) -> List[Importer]:
        """
        Recupera todos los importadores.
        
        Returns:
            List[Importer]: Una lista de objetos Importer.
        """
        all_importers_data = self.storage.get_all(entity_type=self.entity_type)
        return [Importer.from_dict(data) for data in all_importers_data]

    def find_importers_by_country(self, country: str) -> List[Importer]:
        """
        Encuentra importadores por su país de origen.
        
        Args:
            country (str): El país de origen a buscar.
        Returns:
            List[Importer]: Una lista de objetos Importer de ese país.
        """
        importers_data = self.storage.find_by_attribute(entity_type=self.entity_type, attribute="country_of_origin", value=country)
        return [Importer.from_dict(data) for data in importers_data]

    def update_importer(self, importer_id: str, new_data: dict) -> Optional[Importer]:
        """
        Actualiza un importador existente.
        
        Args:
            importer_id (str): El ID del importador a actualizar.
            new_data (dict): Un diccionario con los datos a actualizar.
        Returns:
            Importer | None: El objeto Importer actualizado, o None si falla.
        """
        existing_importer_data = self.storage.get_by_id(entity_type=self.entity_type, item_id=importer_id)
        if not existing_importer_data:
            logger.warning(f"No se encontró el importador con ID {importer_id} para actualizar.")
            return None
        
        existing_importer_data.update(new_data) # Actualiza el diccionario existente
        
        try:
            saved_data = self.storage.save_entity(entity_type=self.entity_type, item_data=existing_importer_data)
            if saved_data:
                logger.info(f"Importador con ID {importer_id} actualizado.")
                return Importer.from_dict(saved_data)
            return None
        except Exception as e:
            logger.error(f"Error al actualizar importador con ID {importer_id}: {e}")
            return None

    def delete_importer(self, importer_id: str) -> bool:
        """
        Elimina un importador por su ID.
        
        Args:
            importer_id (str): El ID del importador a eliminar.
        Returns:
            bool: True si el importador fue eliminado, False si no se encontró.
        """
        try:
            return self.storage.delete_entity(entity_type=self.entity_type, item_id=importer_id)
        except Exception as e:
            logger.error(f"Error al eliminar importador con ID {importer_id}: {e}")
            return False