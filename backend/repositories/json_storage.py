#backend/repositories/json_storage.py
import json
import os
from threading import Lock # Para asegurar la seguridad de hilos al acceder al archivo

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
        # Subimos dos niveles para llegar a la raíz del proyecto (backend/repositories -> backend -> Clear_Pass_proyecto)
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        # AHORA AÑADIMOS 'database' a la ruta para llegar a Clear_Pass_proyecto/database/data.json
        self._data_file = os.path.join(project_root, 'database', data_file) 
        self._data = {}
        self._lock = Lock()
        self._load_data

    def _load_data(self):
        """
        Carga los datos desde el archivo JSON al diccionario en memoria.
        Si el archivo no existe o está vacío, inicializa _data como un diccionario vacío.
        """
        with self._lock: # Asegura que solo un hilo acceda al archivo a la vez
            if os.path.exists(self._data_file) and os.path.getsize(self._data_file) > 0:
                try:
                    with open(self._data_file, 'r', encoding='utf-8') as f:
                        self._data = json.load(f)
                except json.JSONDecodeError:
                    # Si el archivo está corrupto o mal formado JSON, lo inicializa vacío.
                    # Considera añadir logging para errores en un entorno de producción.
                    print(f"Advertencia: El archivo '{self._data_file}' está corrupto o vacío. Se inicializará con datos vacíos.")
                    self._data = {}
            else:
                self._data = {}
            # Asegura que todas las claves de entidad esperadas existan como listas vacías
            # al inicializar, para evitar errores de KeyError más adelante.
            # Esto es un ejemplo, puedes añadir más tipos de entidades si lo necesitas.
            for entity_type in ['users', 'shopping_carts', 'orders', 'payment_methods']:
                if entity_type not in self._data:
                    self._data[entity_type] = []

    def _save_data(self):
        """
        Guarda los datos del diccionario en memoria de vuelta al archivo JSON.
        """
        with self._lock: # Asegura que solo un hilo acceda al archivo a la vez
            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)

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
            # Retorna una copia para evitar modificaciones externas directas a la caché
            return list(self._data.get(entity_type, []))

    def save_entity(self, entity_type: str, entity_data: dict):
        """
        Guarda o actualiza una entidad. Si la entidad ya existe (por su 'id'), la actualiza.
        De lo contrario, la añade.

        Args:
            entity_type (str): La clave del tipo de entidad.
            entity_data (dict): El diccionario que representa la entidad a guardar.
                                Debe contener una clave 'id'.
        Raises:
            ValueError: Si entity_data no contiene una clave 'id'.
        """
        if 'id' not in entity_data:
            raise ValueError("Entity data must contain an 'id' key.")

        with self._lock:
            if entity_type not in self._data:
                self._data[entity_type] = []

            found = False
            for i, existing_entity in enumerate(self._data[entity_type]):
                if existing_entity.get('id') == entity_data['id']:
                    self._data[entity_type][i] = entity_data # Actualiza la entidad existente
                    found = True
                    break
            if not found:
                self._data[entity_type].append(entity_data) # Añade nueva entidad
            self._save_data() # Guarda los cambios al disco

    def get_by_id(self, entity_type: str, entity_id: str) -> dict | None:
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
                self._save_data() # Guarda los cambios al disco solo si hubo una eliminación
                return True
            return False

    def find_by_attribute(self, entity_type: str, attribute: str, value: any) -> list:
        """
        Encuentra entidades que coinciden con un atributo y valor específicos.

        Args:
            entity_type (str): La clave del tipo de entidad.
            attribute (str): El nombre del atributo por el que buscar.
            value (any): El valor del atributo a comparar.

        Returns:
            list: Una lista de diccionarios que representan las entidades encontradas.
        """
        with self._lock:
            results = [
                entity for entity in self._data.get(entity_type, [])
                if entity.get(attribute) == value
            ]
            return results