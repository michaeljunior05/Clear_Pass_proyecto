# backend/models/product.py
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class Product:
    """
    Modelo de datos para un producto.
    """
    def __init__(self, _id=None, name: str = None, price: float = None,
                 description: str = None, category: str = None,
                 image_url: str = None, rating: Dict[str, Any] = None, # Acepta el diccionario de rating
                 external_id: Optional[int] = None, # Cambiado a Optional[int] si los IDs externos son numéricos
                 origin: Optional[str] = None): # Nuevo atributo para el origen
        """
        Inicializa una instancia de Product.

        Args:
            _id (str, optional): ID interno del producto. Si es None, se genera un UUID.
            name (str): Nombre del producto.
            price (float): Precio del producto.
            description (str): Descripción del producto.
            category (str): Categoría del producto.
            image_url (str): URL de la imagen del producto.
            rating (dict): Diccionario con la calificación (ej. {'rate': 3.9, 'count': 120}).
            external_id (int, optional): ID del producto en la API externa, si aplica.
            origin (str, optional): Fuente de donde proviene el producto (ej. 'FakeStoreAPI').
        """
        self._id = str(uuid.uuid4()) if _id is None else _id
        self._name = name
        self._price = price
        self._description = description
        self._category = category
        self._image_url = image_url
        self._rating = rating if rating is not None else {'rate': 0.0, 'count': 0}
        self._external_id = external_id 
        self._origin = origin # Almacenar el origen
        self._created_at = datetime.now().isoformat()
        self._updated_at = datetime.now().isoformat()

    # --- Properties (getters y setters) ---
    @property
    def id(self):
        return self._id

    @property
    def external_id(self):
        return self._external_id

    @external_id.setter
    def external_id(self, value):
        self._external_id = value
        self._updated_at = datetime.now().isoformat()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._updated_at = datetime.now().isoformat()

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value
        self._updated_at = datetime.now().isoformat()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._updated_at = datetime.now().isoformat()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value
        self._updated_at = datetime.now().isoformat()

    @property
    def image_url(self):
        return self._image_url

    @image_url.setter
    def image_url(self, value):
        self._image_url = value
        self._updated_at = datetime.now().isoformat()

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value: Dict[str, Any]): # Asegurar que el setter también espera un dict
        if not isinstance(value, dict) or 'rate' not in value or 'count' not in value:
            # Puedes manejar esto como un error o asignar un valor predeterminado
            self._rating = {'rate': 0.0, 'count': 0}
            # logger.warning("Formato de rating inválido. Usando valor predeterminado.")
        else:
            self._rating = value
        self._updated_at = datetime.now().isoformat()

    @property
    def origin(self): # Nuevo getter para origin
        return self._origin

    @origin.setter # Nuevo setter para origin
    def origin(self, value):
        self._origin = value
        self._updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto Product a un diccionario serializable para JSON.
        """
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "category": self.category,
            "image_url": self.image_url, 
            "rating": self.rating, # rating ya es un diccionario
            "external_id": self.external_id,
            "origin": self.origin, # Incluir el origen
            "created_at": self._created_at,
            "updated_at": self._updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Crea una instancia de Product a partir de un diccionario (ej. de una API externa).
        Mapea los nombres de campo de la API a los atributos del modelo.
        """
        # Mapeo de campos de la API externa (FakeStoreAPI) a nuestros atributos
        # FakeStoreAPI usa 'id', 'title', 'price', 'description', 'category', 'image', 'rating'
        _id = data.get("id") 
        name = data.get("title") # FakeStoreAPI usa 'title' para el nombre
        price = data.get("price")
        description = data.get("description")
        category = data.get("category")
        image_url = data.get("image") # FakeStoreAPI usa 'image' para la URL de la imagen
        rating_data = data.get("rating") # Obtener el diccionario de rating completo

        # --- VALIDACIÓN CLAVE AQUÍ ---
        # Lista de campos esenciales que deben estar presentes y no ser None
        essential_fields = {
            "id": _id,
            "name": name,
            "price": price,
            "description": description,
            "category": category,
            "image_url": image_url
        }

        for field_name, field_value in essential_fields.items():
            if field_value is None:
                # Podrías querer loggear esto en lugar de lanzar una excepción para datos faltantes
                raise ValueError(f"Datos incompletos para crear un producto. Falta el campo esencial '{field_name}'. Datos originales: {data}")
        
        # Convertir price a float de forma segura
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"El precio del producto no es un número válido: '{price}'. Datos originales: {data}")

        # Manejar el rating: si no es un diccionario o es None, usar el valor por defecto
        if not isinstance(rating_data, dict):
            rating_data = {'rate': 0.0, 'count': 0}
        else:
            # Asegurarse de que 'rate' y 'count' son los tipos correctos dentro de rating
            try:
                rating_data['rate'] = float(rating_data.get('rate', 0.0))
                rating_data['count'] = int(rating_data.get('count', 0))
            except (ValueError, TypeError):
                # Si el formato del rating es incorrecto, usar el valor por defecto
                rating_data = {'rate': 0.0, 'count': 0}

        # Crear la instancia de Product usando los nombres de argumento del constructor
        return cls(
            _id=str(_id), # Asegurarse de que el ID es un string para nuestro ID interno
            name=name,
            price=price,
            description=description,
            category=category,
            image_url=image_url, 
            rating=rating_data, # Pasar el diccionario de rating completo
            external_id=_id, # Usar el ID original de la API como external_id
            origin="FakeStoreAPI" # Asignar el origen
        )

    def __repr__(self):
        return f"<Product {self.name} (ID: {self.id})>"

