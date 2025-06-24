# backend/repositories/json_storage.py
import os
import json
import uuid # Necesario para generar IDs si no se proporcionan
import logging
from threading import Lock # Para asegurar la seguridad de hilos al acceder al archivo
from typing import Any, Optional

logger = logging.getLogger(__name__) # Instancia de logger para este módulo

class JSONStorage:
    """
    Clase para manejar la persistencia de datos en un archivo JSON.
    Actúa como una base de datos simple para almacenar diferentes tipos de entidades.
    Cada tipo de entidad (ej. 'users', 'products') se almacena como una lista
    de diccionarios bajo una clave en el diccionario JSON principal.
    """
    def __init__(self, data_file='data.json'):
        """
        Inicializa el almacenamiento JSON.

        Args:
            data_file (str): El nombre del archivo JSON. Por defecto, 'data.json'.
                                La ruta completa se construirá basada en la estructura del proyecto.
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        self._data_file = os.path.join(project_root, 'database', data_file) 
        
        self._lock = Lock() 
        
        self._ensure_db_file_exists() 
        
        with self._lock: 
            self._data = self._load_data() 
        logger.info(f"JSONStorage inicializado. Datos cargados desde {self._data_file}.")


    def _ensure_db_file_exists(self):
        """
        Asegura que el directorio de la base de datos y el archivo JSON existen.
        Si el archivo no existe, lo crea con un objeto JSON vacío.
        """
        db_dir = os.path.dirname(self._data_file)
        if not os.path.exists(db_dir):
            logger.info(f"Creando directorio para la base de datos: {db_dir}")
            os.makedirs(db_dir) 

        if not os.path.exists(self._data_file):
            logger.info(f"Creando archivo de base de datos vacío en: {self._data_file}")
            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f) 


    def _load_data(self) -> dict:
        """
        Carga los datos desde el archivo JSON al diccionario en memoria.
        Si el archivo no existe o está vacío/corrupto, inicializa los datos como un diccionario vacío.
        """
        logger.info(f"Cargando datos desde: {self._data_file}")
        try:
            if not os.path.exists(self._data_file) or os.path.getsize(self._data_file) == 0:
                logger.warning(f"El archivo '{self._data_file}' no existe o está vacío. Inicializando con datos vacíos.")
                self._ensure_db_file_exists() 
                return {}
            
            with open(self._data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Datos cargados exitosamente desde '{self._data_file}'.")
                if not isinstance(data, dict): 
                        logger.warning(f"El contenido de '{self._data_file}' no es un diccionario. Inicializando con datos vacíos.")
                        return {}
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON desde '{self._data_file}': {e}. Se inicializará con datos vacíos.")
            return {}
        except FileNotFoundError:
            logger.warning(f"Archivo de base de datos no encontrado en '{self._data_file}'. Se inicializará con datos vacíos.")
            self._ensure_db_file_exists()
            return {}
        except Exception as e:
            logger.critical(f"Error inesperado al cargar datos desde '{self._data_file}': {e}")
            raise 


    def _save_data(self, data: dict):
        """
        Guarda los datos del diccionario en memoria de vuelta al archivo JSON.
        """
        logger.info(f"Guardando datos en {self._data_file}...")
        try:
            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Datos guardados exitosamente en {self._data_file}.")
        except IOError as e:
            logger.critical(f"ERROR CRÍTICO: Fallo de E/S al guardar datos en '{self._data_file}': {e}")
            raise 
        except Exception as e:
            logger.critical(f"ERROR CRÍTICO: Fallo inesperado al guardar datos en '{self._data_file}': {e}")
            raise 


    def get_all(self, entity_type: str) -> list:
        """
        Recupera todas las entidades de un tipo específico.

        Args:
            entity_type (str): La clave del tipo de entidad (ej. 'users', 'products').

        Returns:
            list: Una lista de diccionarios que representan las entidades.
                    Retorna una lista vacía si el tipo de entidad no existe.
        """
        with self._lock:
            if entity_type not in self._data:
                self._data[entity_type] = [] 
            return list(self._data.get(entity_type, []))


    def save_entity(self, entity_type: str, entity_data: dict) -> dict:
        """
        Guarda o actualiza una entidad. Si la entidad ya existe (por su 'id'), la actualiza.
        De lo contrario, la añade.

        Args:
            entity_type (str): La clave del tipo de entidad.
            entity_data (dict): El diccionario que representa la entidad a guardar.
                                Debe contener una clave 'id' o se generará una.
        Returns:
            dict: El diccionario de la entidad guardada (con ID asignado si es nuevo).
        Raises:
            ValueError: Si entity_data no contiene una clave 'id' (y no se pudo generar una).
        """
        logger.info(f"save_entity: Iniciando guardado para tipo '{entity_type}'.")
        
        if 'id' not in entity_data or not entity_data['id']:
            entity_data['id'] = str(uuid.uuid4())
            logger.info(f"save_entity: ID generado para nueva entidad: {entity_data['id']}.")
        
        with self._lock: 
            self._data = self._load_data() 

            if entity_type not in self._data:
                self._data[entity_type] = []
                logger.info(f"save_entity: Creada nueva lista para '{entity_type}'.")

            found = False
            for i, existing_entity in enumerate(self._data[entity_type]):
                if existing_entity.get('id') == entity_data['id']:
                    self._data[entity_type][i] = entity_data 
                    found = True
                    logger.info(f"save_entity: Entidad con ID '{entity_data['id']}' actualizada.")
                    break
            
            if not found:
                self._data[entity_type].append(entity_data) 
                logger.info(f"save_entity: Entidad con ID '{entity_data['id']}' añadida.")
            
            try:
                self._save_data(self._data) 
                logger.info(f"save_entity: Proceso de guardado completado para ID: {entity_data['id']}.")
            except Exception as e:
                logger.error(f"ERROR CRÍTICO: Fallo en self._save_data dentro de save_entity: {e}")
                raise 
        
        return entity_data


    def get_by_id(self, entity_type: str, entity_id: str) -> Optional[dict]:
        """
        Recupera una entidad por su ID.

        Args:
            entity_type (str): La clave del tipo de entidad.
            entity_id (str): El ID de la entidad a buscar.

        Returns:
            dict | None: El diccionario que representa la entidad si se encuentra,
                            None si no se encuentra.
        """
        with self._lock:
            if entity_type not in self._data:
                return None 
            
            for entity in self._data.get(entity_type, []):
                if entity.get('id') == entity_id:
                    return entity
            return None


    def delete_entity(self, entity_type: str, entity_id: str) -> bool:
        """
        Elimina una entidad por su ID.

        Args:
            entity_type (str): La clave del tipo de entidad.
            entity_id (str): El ID de la entidad a eliminar.

        Returns:
            bool: True si la entidad fue eliminada exitosamente, False si no se encontró.
        """
        with self._lock:
            if entity_type not in self._data:
                return False

            original_len = len(self._data[entity_type])
            self._data[entity_type] = [
                entity for entity in self._data[entity_type]
                if entity.get('id') != entity_id
            ]
            if len(self._data[entity_type]) < original_len:
                self._save_data(self._data) 
                logger.info(f"Entidad con ID '{entity_id}' eliminada de '{entity_type}'.")
                return True
            logger.info(f"Entidad con ID '{entity_id}' no encontrada para eliminar en '{entity_type}'.")
            return False


    def find_by_attribute(self, entity_type: str, attribute: str, value: Any) -> list:
        """
        Encuentra entidades que coinciden con un atributo y valor específicos.

        Args:
            entity_type (str): La clave del tipo de entidad.
            attribute (str): El nombre del atributo por el que buscar.
            value (Any): El valor del atributo a comparar.

        Returns:
            list: Una lista de diccionarios que representan las entidades encontradas.
        """
        with self._lock:
            if entity_type not in self._data:
                return [] 
            
            results = [
                entity for entity in self._data.get(entity_type, [])
                if entity.get(attribute) == value
            ]
            return results
    